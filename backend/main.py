"""
main.py
-------
FastAPI application entry point.

Start dev server:
    uvicorn main:app --reload --port 8000

API docs auto-generated at:
    http://localhost:8000/docs    (Swagger UI)
    http://localhost:8000/redoc  (ReDoc)
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.chat import router as chat_router
from app.api.lead import router as lead_router
from app.api.voice import router as voice_router
from app.rag.retriever import get_vector_store
from app.utils.database import init_db

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup/shutdown hooks) ────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Nodus AI backend...")

    # Initialize PostgreSQL tables only — fast, no blocking
    init_db()
    logger.info("Loading ChromaDB and embedding model...")
    get_vector_store()
    logger.info("✅ Backend ready — ChromaDB loads on first request")
    yield
    logger.info("👋 Shutting down Nodus AI backend")


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="Nodus Decoded AI Backend",
    description="RAG-powered chatbot API for Nodus Decoded",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.app_env == "development" else None,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat_router)
app.include_router(lead_router)
app.include_router(voice_router)

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check():
    store = get_vector_store()
    return {
        "status": "ok",
        "chroma_loaded": store is not None,
        "timestamp": datetime.utcnow().isoformat(),
        "env": settings.app_env,
    }


@app.get("/", tags=["root"])
async def root():
    return {"message": "Nodus AI API is running. See /docs for endpoints."}