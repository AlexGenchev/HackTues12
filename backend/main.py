# backend/main.py
# FastAPI application entry point for the Smart Box backend.
# Run with: uvicorn backend.main:app --reload

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

# Configure logging before importing any project modules so that all loggers
# inherit the same configuration.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from backend.database import engine, Base  # noqa: E402 — must be after load_dotenv
from backend.routes.complaints import router as complaints_router, UPLOAD_DIR  # noqa: E402

# Create all database tables on startup.
Base.metadata.create_all(bind=engine)
logger.info("Database tables ensured.")

app = FastAPI(
    title="Smart Box — Civic Complaint API",
    description=(
        "Backend API for the Smart Box civic complaint system. "
        "Citizens record voice complaints on a Raspberry Pi; this backend "
        "transcribes, classifies, formalises, and routes them to the correct "
        "municipal department."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded audio files as static assets (useful for the admin frontend).
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=UPLOAD_DIR), name="audio")

# Register routers.
app.include_router(complaints_router)


@app.get("/", tags=["health"])
def health_check():
    """Basic health-check endpoint."""
    return {"status": "ok", "service": "Smart Box Backend"}
