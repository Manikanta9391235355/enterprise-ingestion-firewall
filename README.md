# Enterprise Structured Ingestion Firewall

An AI-powered enterprise support assistant built using FastAPI, OpenRouter, Python, HTML, CSS, and JavaScript.

The application analyzes incoming messages, generates structured JSON metadata, and provides context-aware AI responses with conversation memory.

## Features

- Intent detection and classification
- Risk profiling and priority scoring
- Token usage tracking
- Context-aware AI responses using OpenRouter
- Session-based conversation memory
- Independent chat sessions using UUIDs
- New Chat functionality
- Markdown response rendering
- Responsive HTML, CSS, and JavaScript interface
- FastAPI REST endpoints and Pydantic validation
- API error handling

## Tech Stack

**Backend:** Python, FastAPI, Pydantic

**Frontend:** HTML, CSS, JavaScript

**LLM:** OpenRouter API

**Conversation Memory:** Python dictionary and UUID

## Project Structure

```text
enterprise-ingestion-firewall/
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── firewall.py
│   ├── llm_service.py
│   └── memory.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/enterprise-ingestion-firewall.git
cd enterprise-ingestion-firewall
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure OpenRouter

Create a `.env` file using `.env.example` as a reference.

```dotenv
OPENROUTER_API_KEY=your_actual_api_key
OPENROUTER_MODEL=openrouter/free
```

### 5. Run the application

```bash
python -m uvicorn backend.main:app --reload
```

Open the application at:

http://127.0.0.1:8000/

API documentation:

http://127.0.0.1:8000/docs

## Application Workflow

User Message → FastAPI → Intent Classification → Risk & Priority Analysis → Session History → OpenRouter LLM → AI Response → HTML Interface

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Web interface |
| GET | `/health` | Health check |
| POST | `/sessions` | Create a new session |
| GET | `/sessions/{session_id}` | Retrieve chat history |
| DELETE | `/sessions/{session_id}` | Delete a session |
| POST | `/chat` | Analyze message and generate response |

## Conversation Memory

Each conversation receives a unique session ID.

Previous messages are stored in memory and sent to the LLM to generate context-aware responses.

Starting a new chat creates an independent conversation.

**Note:** Conversation history is stored in memory and is cleared when the backend restarts.

## Security and Limitations

- API keys are loaded from environment variables.
- Pydantic validates incoming requests and structured responses.
- Risk classification is AI-assisted and should not be treated as a standalone security control.
- This project is a local development prototype. Production deployment requires authentication, persistent storage, rate limiting, and additional security controls.

## Author

Manikanta Galipalli

AI Automation Engineer | Python | FastAPI | AI Agents | LLM Applications
