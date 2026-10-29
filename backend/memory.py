
from uuid import uuid4
from threading import RLock

sessions = {}
lock = RLock()

MAX_HISTORY_MESSAGES = 8


def create_session():
    session_id = str(uuid4())

    with lock:
        sessions[session_id] = []

    return session_id


def session_exists(session_id: str):
    with lock:
        return session_id in sessions


def get_history(session_id: str):
    with lock:
        if session_id not in sessions:
            raise KeyError("Session not found")

        return [
            item.copy()
            for item in sessions[session_id][-MAX_HISTORY_MESSAGES:]
        ]


def add_message(session_id: str, role: str, content: str):
    with lock:
        if session_id not in sessions:
            raise KeyError("Session not found")

        sessions[session_id].append({
            "role": role,
            "content": content,
        })


def delete_session(session_id: str):
    with lock:
        return sessions.pop(session_id, None) is not None
