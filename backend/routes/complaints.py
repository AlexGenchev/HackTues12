# backend/routes/complaints.py
# FastAPI router for all /complaints endpoints.
# Orchestrates the full AI pipeline: transcription → classification →
# municipality lookup → formalization → email → database.

import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Complaint
from backend.data.municipalities import lookup_municipality
from backend.data.department_emails import get_department_email
from backend.services.transcription import transcribe_audio
from backend.services.classification import classify_complaint
from backend.services.formalization import formalize_complaint
from backend.services.email_service import send_complaint_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/complaints", tags=["complaints"])

# Directory where uploaded audio files are temporarily stored.
UPLOAD_DIR = os.getenv(
    "UPLOAD_DIR",
    os.path.join(os.path.dirname(__file__), "..", "uploaded_audio"),
)
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# POST /complaints/upload — full AI pipeline
# ---------------------------------------------------------------------------

@router.post("/upload")
async def upload_complaint(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Accept a WAV audio file and run the full complaint processing pipeline.

    Steps:
        1. Save audio file to disk.
        2. Transcribe with Groq Whisper (Bulgarian).
        3. Classify complaint (category, location, urgency).
        4. Look up municipality from location.
        5. Formalize complaint letter.
        6. Determine recipient email.
        7. Send email.
        8. Persist complaint to database.
        9. Return structured JSON response.
    """

    # ------------------------------------------------------------------
    # Step 1 — Save audio file
    # ------------------------------------------------------------------
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe_name = f"{timestamp}_{uuid.uuid4().hex[:8]}.wav"
    audio_path = os.path.join(UPLOAD_DIR, safe_name)

    try:
        contents = await audio_file.read()
        with open(audio_path, "wb") as f:
            f.write(contents)
        logger.info("Audio saved: %s (%d bytes)", audio_path, len(contents))
    except Exception as exc:
        logger.error("Failed to save audio file: %s", exc)
        return {
            "status": "error",
            "step_failed": "save_audio",
            "detail": str(exc),
        }

    # ------------------------------------------------------------------
    # Step 2 — Speech-to-text transcription
    # ------------------------------------------------------------------
    try:
        transcribed_text = await transcribe_audio(audio_path)
        # Delete audio file after successful transcription to save disk space.
        try:
            os.remove(audio_path)
            logger.info("Audio file deleted after transcription: %s", audio_path)
        except OSError as del_exc:
            logger.error("Could not delete audio file %s: %s", audio_path, del_exc)
    except Exception as exc:
        logger.error("Transcription failed: %s", exc)
        # Keep the file on disk for debugging when transcription fails.
        return {
            "status": "error",
            "step_failed": "transcription",
            "detail": str(exc),
        }

    # ------------------------------------------------------------------
    # Step 3 — Complaint classification
    # ------------------------------------------------------------------
    try:
        classification = await classify_complaint(transcribed_text)
        category: str = classification["category"]
        location_mentioned: Optional[str] = classification["location_mentioned"]
        urgency: str = classification["urgency"]
    except Exception as exc:
        logger.error("Classification failed: %s", exc)
        return {
            "status": "error",
            "step_failed": "classification",
            "detail": str(exc),
        }

    # ------------------------------------------------------------------
    # Step 4 — Municipality lookup
    # ------------------------------------------------------------------
    municipality_info = None
    municipality_name: Optional[str] = None
    if location_mentioned:
        municipality_info = lookup_municipality(location_mentioned)
        if municipality_info:
            municipality_name = municipality_info.get("municipality")

    logger.info(
        "Municipality lookup: location=%s → municipality=%s",
        location_mentioned,
        municipality_name,
    )

    # ------------------------------------------------------------------
    # Step 5 — Formalize complaint letter
    # ------------------------------------------------------------------
    try:
        formal_letter = await formalize_complaint(
            transcribed_text=transcribed_text,
            category=category,
            location=location_mentioned,
            municipality=municipality_name,
            urgency=urgency,
        )
    except Exception as exc:
        logger.error("Formalization failed: %s", exc)
        return {
            "status": "error",
            "step_failed": "formalization",
            "detail": str(exc),
        }

    # ------------------------------------------------------------------
    # Step 6 — Determine recipient email
    # ------------------------------------------------------------------
    try:
        sent_to_email = get_department_email(category, municipality_name)
        logger.info("Recipient email resolved: %s", sent_to_email)
    except Exception as exc:
        logger.error("Email lookup failed: %s", exc)
        return {
            "status": "error",
            "step_failed": "email_lookup",
            "detail": str(exc),
        }

    # ------------------------------------------------------------------
    # Step 7 — Send email (failure here does NOT abort the pipeline)
    # ------------------------------------------------------------------
    email_sent = False
    try:
        email_sent = send_complaint_email(
            to_email=sent_to_email,
            subject=f"[СИГНАЛ][{category}][{urgency}] Гражданска жалба",
            body=formal_letter,
            category=category,
            urgency=urgency,
        )
    except Exception as exc:
        # Log but continue — we still want to save to the database.
        logger.error("Email send raised unexpected exception: %s", exc)

    # ------------------------------------------------------------------
    # Step 8 — Persist to database
    # ------------------------------------------------------------------
    try:
        complaint = Complaint(
            audio_filename=safe_name,
            transcribed_text=transcribed_text,
            category=category,
            location_mentioned=location_mentioned,
            urgency=urgency,
            formal_letter=formal_letter,
            sent_to_email=sent_to_email,
            email_sent_successfully=email_sent,
            processing_error=None,
        )
        db.add(complaint)
        db.commit()
        db.refresh(complaint)
        logger.info("Complaint saved to database with id=%d", complaint.id)
    except Exception as exc:
        logger.error("Database save failed: %s", exc)
        return {
            "status": "error",
            "step_failed": "database",
            "detail": str(exc),
        }

    # ------------------------------------------------------------------
    # Step 9 — Return success response
    # ------------------------------------------------------------------
    return {
        "status": "success",
        "transcribed_text": transcribed_text,
        "category": category,
        "urgency": urgency,
        "municipality": municipality_name,
        "sent_to_email": sent_to_email,
        "email_sent": email_sent,
        "complaint_id": complaint.id,
    }


# ---------------------------------------------------------------------------
# GET /complaints — paginated list
# ---------------------------------------------------------------------------

@router.get("")
def get_complaints(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """Return a paginated list of all complaints, newest first."""
    offset = (page - 1) * limit
    total = db.query(Complaint).count()
    items = (
        db.query(Complaint)
        .order_by(Complaint.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "limit": limit,
        "items": [_complaint_to_dict(c) for c in items],
    }


# ---------------------------------------------------------------------------
# GET /complaints/{id} — single complaint
# ---------------------------------------------------------------------------

@router.get("/{complaint_id}")
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """Return detail for a single complaint by its database ID."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Сигналът не е намерен.")
    return _complaint_to_dict(complaint, include_letter=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _complaint_to_dict(complaint: Complaint, include_letter: bool = False) -> dict:
    """Serialise a Complaint ORM object to a plain dictionary."""
    data = {
        "id": complaint.id,
        "created_at": complaint.created_at.isoformat() if complaint.created_at else None,
        "audio_filename": complaint.audio_filename,
        "transcribed_text": complaint.transcribed_text,
        "category": complaint.category,
        "location_mentioned": complaint.location_mentioned,
        "urgency": complaint.urgency,
        "sent_to_email": complaint.sent_to_email,
        "email_sent_successfully": complaint.email_sent_successfully,
        "processing_error": complaint.processing_error,
    }
    if include_letter:
        data["formal_letter"] = complaint.formal_letter
    return data
