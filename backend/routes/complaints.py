import os, uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Complaint
from backend.data.municipalities import lookup_municipality
from backend.data.department_emails import get_department_email
from backend.services.transcription import transcribe_audio
from backend.services.classification import classify_complaint
from backend.services.formalization import formalize_complaint
from backend.services.email_service import send_complaint_email

router = APIRouter(prefix="/complaints", tags=["complaints"])
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploaded_audio")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    
    with open(audio_path, "wb") as f: f.write(await audio_file.read())
        
    try:
        text = await transcribe_audio(audio_path)
        os.remove(audio_path)
        cls = await classify_complaint(text)
        mun_info = lookup_municipality(cls["location_mentioned"]) if cls["location_mentioned"] else None
        mun_name = mun_info.get("municipality") if mun_info else None
        
        formal = await formalize_complaint(text, cls["category"], cls["location_mentioned"], mun_name, cls["urgency"])
        email = get_department_email(cls["category"], mun_name)
        sent = send_complaint_email(email, "", formal, cls["category"], cls["urgency"])
        
        c = Complaint(
            audio_filename=safe_name, transcribed_text=text, category=cls["category"],
            location_mentioned=cls["location_mentioned"], urgency=cls["urgency"],
            formal_letter=formal, sent_to_email=email, email_sent_successfully=sent
        )
        db.add(c); db.commit(); db.refresh(c)
        return {"status": "success", "transcribed_text": text, "category": cls["category"], "urgency": cls["urgency"], "municipality": mun_name, "complaint_id": c.id}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@router.get("")
def get_complaints(page: int = 1, limit: int = 20, db: Session = Depends(get_db)):
    items = db.query(Complaint).order_by(Complaint.created_at.desc()).offset((page - 1) * limit).limit(limit).all()
    return {"total": db.query(Complaint).count(), "items": [to_dict(c) for c in items], "page": page, "limit": limit}

@router.get("/{id}")
def get_complaint(id: int, db: Session = Depends(get_db)):
    c = db.query(Complaint).filter(Complaint.id == id).first()
    if not c: raise HTTPException(404, "Not found")
    return to_dict(c)

