import os, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Complaint
from backend.data.municipalities import lookup_municipality
from backend.data.department_emails import get_department_email
from backend.services.transcription import transcribe_audio
from backend.services.classification import classify_complaint
from backend.services.formalization import formalize_complaint
from backend.services.email_service import send_complaint_email
from backend.services.vik_form import fill_vik_form

router = APIRouter(prefix="/complaints", tags=["complaints"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class SendEmailPayload(BaseModel):
    to: str
    subject: str
    body: str

class TextComplaintPayload(BaseModel):
    text: str


def to_dict(c):
    return {
        "id": c.id, "created_at": c.created_at.isoformat() if c.created_at else None,
        "audio_filename": c.audio_filename, "transcribed_text": c.transcribed_text,
        "category": c.category, "location_mentioned": c.location_mentioned,
        "urgency": c.urgency, "sent_to_email": c.sent_to_email,
        "email_sent_successfully": c.email_sent_successfully,
        "formal_letter": c.formal_letter
    }


@router.post("/upload")
async def upload_complaint(audio_file: UploadFile = File(...), db: Session = Depends(get_db)):
    safe_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.wav"
    audio_path = os.path.join(UPLOAD_DIR, safe_name)

    with open(audio_path, "wb") as f:
        f.write(await audio_file.read())

    try:
        text = await transcribe_audio(audio_path)
        cls = await classify_complaint(text)
        mun_info = lookup_municipality(cls["location_mentioned"]) if cls["location_mentioned"] else None
        mun_name = mun_info.get("municipality") if mun_info else None

        formal = await formalize_complaint(text, cls["category"], cls["location_mentioned"], mun_name, cls["urgency"])

        if cls["category"] == "WATER_SUPPLY":
            sent = await fill_vik_form(text)
            email = "https://viksofbg.com/signal/"
        else:
            email = get_department_email(cls["category"], mun_name)
            sent = False  # sent manually from admin panel

        c = Complaint(
            audio_filename=safe_name, transcribed_text=text, category=cls["category"],
            location_mentioned=cls["location_mentioned"], urgency=cls["urgency"],
            formal_letter=formal, sent_to_email=email, email_sent_successfully=sent
        )
        db.add(c); db.commit(); db.refresh(c)
        return {"status": "success", "transcribed_text": text, "category": cls["category"],
                "urgency": cls["urgency"], "municipality": mun_name, "complaint_id": c.id}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)


@router.post("/test-text")
async def test_text_complaint(payload: TextComplaintPayload, db: Session = Depends(get_db)):
    text = payload.text
    """Test endpoint — submit plain text instead of audio, runs the full pipeline."""
    try:
        cls = await classify_complaint(text)
        mun_info = lookup_municipality(cls["location_mentioned"]) if cls["location_mentioned"] else None
        mun_name = mun_info.get("municipality") if mun_info else None
        formal = await formalize_complaint(text, cls["category"], cls["location_mentioned"], mun_name, cls["urgency"])

        if cls["category"] == "WATER_SUPPLY":
            sent = await fill_vik_form(text)
            email = "https://viksofbg.com/signal/"
        else:
            email = get_department_email(cls["category"], mun_name)
            sent = False  # sent manually from admin panel

        c = Complaint(
            transcribed_text=text, category=cls["category"],
            location_mentioned=cls["location_mentioned"], urgency=cls["urgency"],
            formal_letter=formal, sent_to_email=email, email_sent_successfully=sent
        )
        db.add(c); db.commit(); db.refresh(c)
        return {"status": "success", "category": cls["category"], "urgency": cls["urgency"],
                "municipality": mun_name, "complaint_id": c.id, "formal_letter": formal}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/emails/pending")
def get_pending_emails(db: Session = Depends(get_db)):
    items = db.query(Complaint).filter(
        Complaint.email_sent_successfully == False,
        ~Complaint.sent_to_email.like("%viksofbg%")
    ).order_by(Complaint.created_at.desc()).all()
    return [to_dict(c) for c in items]


@router.post("/{id}/send-email")
def send_email_manually(id: int, payload: SendEmailPayload, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.id == id).first()
    if not c:
        raise HTTPException(404, "Not found")
    ok = send_complaint_email(payload.to, payload.subject, payload.body, c.category, c.urgency)
    if not ok:
        raise HTTPException(500, "Неуспешно изпращане — провери EMAIL_SENDER и EMAIL_PASSWORD в .env")
    c.email_sent_successfully = True
    c.sent_to_email = payload.to
    db.commit()
    return {"status": "sent"}


@router.post("/{id}/discard-email")
def discard_email(id: int, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.id == id).first()
    if not c:
        raise HTTPException(404, "Not found")
    c.email_sent_successfully = True
    db.commit()
    return {"status": "discarded"}


@router.get("")
def get_complaints(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    items = db.query(Complaint).order_by(Complaint.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {"total": db.query(Complaint).count(), "items": [to_dict(c) for c in items], "page": page, "limit": limit}


@router.get("/{id}")
def get_complaint(id: int, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.id == id).first()
    if not c:
        raise HTTPException(404, "Not found")
    return to_dict(c)
