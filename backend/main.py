
from contextlib import asynccontextmanager
from collections import defaultdict
from pathlib import Path
import asyncio
import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from openai import APIError, APITimeoutError, RateLimitError

from backend.schemas import ChatRequest, ChatResponse
from backend.firewall import process_message
from backend.llm_service import generate_response
from backend.memory import (
    create_session,
    get_history,
    add_message,
    delete_session,
    session_exists,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

session_locks = defaultdict(asyncio.Lock)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    session_locks.clear()


app = FastAPI(
    title="Enterprise Structured Ingestion Firewall",
    description="AI firewall with conversation memory",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static",
)


@app.get("/")
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/sessions")
def new_session():
    session_id = create_session()
    return {"session_id": session_id}


@app.get("/sessions/{session_id}")
def session_history(session_id: str):
    try:
        history = get_history(session_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    return {
        "session_id": session_id,
        "history": history,
    }


@app.delete("/sessions/{session_id}")
def remove_session(session_id: str):
    if not delete_session(session_id):
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    session_locks.pop(session_id, None)
    return {"message": "Session deleted"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    message = request.message.strip()

    if not message:
        raise HTTPException(
            status_code=422,
            detail="Message cannot be empty",
        )

    session_id = request.session_id

    if session_id is None:
        session_id = create_session()
    elif not session_exists(session_id):
        raise HTTPException(
            status_code=404,
            detail="Session not found",
        )

    async with session_locks[session_id]:
        try:
            history = get_history(session_id)

            firewall = await process_message(message)

            if firewall.risk.level == "high":
                answer = (
                    "This request has been flagged for review. "
                    "Please contact the appropriate support team "
                    "through an official channel."
                )
                answer_usage = None
            else:
                answer, answer_usage = await generate_response(
                    message, history
                )

            if answer_usage:
                firewall.tokens.input_tokens += (
                    answer_usage.prompt_tokens or 0
                )
                firewall.tokens.output_tokens += (
                    answer_usage.completion_tokens or 0
                )
                firewall.tokens.total_tokens = (
                    firewall.tokens.input_tokens
                    + firewall.tokens.output_tokens
                )

            add_message(session_id, "user", message)
            add_message(session_id, "assistant", answer)

            return ChatResponse(
                session_id=session_id,
                response=answer,
                firewall=firewall,
            )

        except (RateLimitError, APITimeoutError):
            raise HTTPException(
                status_code=503,
                detail="AI service temporarily unavailable",
            )
        except APIError:
            logger.exception("OpenRouter API failure")
            raise HTTPException(
                status_code=502,
                detail="AI provider request failed",
            )
        except (ValueError, KeyError):
            logger.exception("Invalid AI response or session")
            raise HTTPException(
                status_code=502,
                detail="Unable to process the AI response",
            )
