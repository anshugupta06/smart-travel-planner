"""
Smart Travel Planner - FastAPI Backend
AI-powered travel planning with LLM + ML hybrid approach.
"""
import sys
import os

# Ensure UTF-8 output on Windows (fixes emoji print crashes)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import init_db
from routers.trip_router import router as trip_router
from routers.history_router import router as history_router
from routers.chat_router import router as chat_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    print("✅ Smart Travel Planner API started")
    print("📖 Docs: http://localhost:8000/docs")
    yield
    print("👋 Shutting down...")


app = FastAPI(
    title="Smart Travel Planner API",
    description="AI-powered travel planning using LLM + ML hybrid approach",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — reads from env var in production, defaults to localhost for development
_raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:4173"
)
ALLOWED_ORIGINS = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Register routers
app.include_router(trip_router)
app.include_router(history_router)
app.include_router(chat_router)


@app.get("/")
async def root():
    return {
        "message": "Smart Travel Planner API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "smart-travel-planner"}
