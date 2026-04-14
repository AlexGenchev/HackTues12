import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

from backend.database import engine, Base  # noqa: E402 — must be after load_dotenv
from backend.routes.complaints import router as complaints_router, UPLOAD_DIR  # noqa: E402

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

os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=UPLOAD_DIR), name="audio")

app.include_router(complaints_router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "service": "Smart Box Backend"}
