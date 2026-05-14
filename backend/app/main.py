from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import appointments, chat, tools

load_dotenv()

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FRONTEND_INDEX = _REPO_ROOT / "frontend" / "index.html"

app = FastAPI(title="Municipality Voicebot API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tools.router)
app.include_router(appointments.router)
app.include_router(chat.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def serve_ui() -> FileResponse:
    """Serve UI from repo `frontend/` (local dev). In Docker Compose use the `frontend` service."""
    if not _FRONTEND_INDEX.is_file():
        raise HTTPException(
            status_code=503,
            detail="Missing frontend/index.html — run from repo with frontend/ present, or open the frontend container URL.",
        )
    return FileResponse(_FRONTEND_INDEX)
