from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
import shutil
import uuid
import os

from app.database import engine, SessionLocal, Base
from app import models, schemas


load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print("GROQ_API_KEY loaded:", bool(os.getenv("GROQ_API_KEY")))

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Box Backend API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UPLOAD_DIR = os.getenv("UPLOAD_DIR", os.path.join(
    os.path.dirname(__file__), "uploaded_audio"))
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/audio", StaticFiles(directory=UPLOAD_DIR), name="audio")


def transcribe_audio(audio_path: str) -> Optional[str]:
    try:
        with open(audio_path, "rb") as audio_file:
            transcript = groq_client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print("Speech-to-text error:", e)
        return None


formal_template = """
Официално регистрационно оплакване

Заглавие: {title}
Категория: {category}
Приоритет: {priority}

Описание на проблема: 
{description}
   
Местоположение: {location}
Подал сигнал: {name}

Моля, вземете необходимите мерки за решаване на проблема.
Благодарим за съдействието.
"""


def process_signal_logic(text: str, name: str, location: str) -> dict:
    text_lower = text.lower()
    category = "Others"
    priority = "Low"
    title = "Общ сигнал"

    if "дупка" in text_lower or "улица" in text_lower or "път" in text_lower:
        category = "Road safety"
        priority = "Medium"
        title = "Проблем с пътната настилка"
    elif "боклук" in text_lower or "смет" in text_lower or "кофа" in text_lower:
        category = "Garbage"
        priority = "Low"
        title = "Проблем с боклука"
    elif "вода" in text_lower or "тръба" in text_lower or "теч" in text_lower:
        category = "Water"
        priority = "High"
        title = "Авария с водопровода"
    elif "лампа" in text_lower or "осветление" in text_lower or "тъмно" in text_lower:
        category = "Lighting"
        priority = "Medium"
        title = "Улично осветление"

    if "спешно" in text_lower or "опасно" in text_lower:
        priority = "High"

    formal_message = formal_template.format(
        title=title,
        category=category,
        priority=priority,
        description=text,
        location=location,
        name=name
    )

    return {
        "title": title,
        "category": category,
        "priority": priority,
        "formal_message": formal_message
    }


def send_email(to_email: str, subject: str, body: str, high_priority: bool = False):
    msg = EmailMessage()
    msg['From'] = os.getenv("SMTP_USER")
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    if high_priority:
        msg['X-Priority'] = '1'
        msg['X-MSMail-Priority'] = 'High'
        msg['Importance'] = 'High'

    try:
        with smtplib.SMTP(os.getenv("SMTP_SERVER"), int(os.getenv("SMTP_PORT"))) as server:
            server.starttls()
            server.login(os.getenv("SMTP_USER"), os.getenv("SMTP_PASSWORD"))
            server.send_message(msg)
        print(f"Email sent to {to_email}, high priority: {high_priority}")
    except Exception as e:
        print("Error sending email:", e)


@app.post("/complaints/upload")
def upload_complaint(
    name: Optional[str] = Form(None),
    location: Optional[str] = Form(None),
    original_text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    processed_text = original_text
    audio_path = None

    if audio_file:
        safe_filename = f"{uuid.uuid4()}_{audio_file.filename}"
        file_location = os.path.join(UPLOAD_DIR, safe_filename)

        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(audio_file.file, file_object)
        audio_path = file_location

        if not processed_text:
            processed_text = transcribe_audio(file_location)

            if not processed_text:
                os.remove(file_location)
                raise HTTPException(
                    status_code=500,
                    detail="Неуспешно разпознаване на аудио."
                )

    if not processed_text:
        raise HTTPException(
            status_code=400,
            detail="Не е предоставен текст или аудио."
        )

    ai_data = process_signal_logic(
        processed_text,
        name=name if name else "Анонимен",
        location=location if location else "Неуточнено"
    )

    new_complaint = models.Complaint(
        name=name,
        location=location,
        title=ai_data["title"],
        original_message=processed_text,
        formal_message=ai_data["formal_message"],
        category=ai_data["category"],
        priority=ai_data["priority"],
        status="New",
        audio_path=audio_path
    )

    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    category_to_email = {
        "Road safety": "v.nacheva@api.bg",  # Glaven sekretar
        "Garbage": "inspectorat@inspectorat-so.org",
        "Water": "dker@dker.bg",
        "Lighting": "dker@dker.bg"
    }

    recipient_email = category_to_email.get(new_complaint.category, "")
    high_priority_flag = True if new_complaint.priority == "High" else False

    if recipient_email:
        send_email(
            to_email=recipient_email,
            subject=f"Нов сигнал: {new_complaint.title}",
            body=new_complaint.formal_message,
            high_priority=high_priority_flag
        )
    else:
        print(f"Няма дефиниран имейл за категория {new_complaint.category}")

    return {
        "success": True,
        "recognised_text": processed_text,
        "complaint_id": new_complaint.id,
        "generated_data": {
            "name": new_complaint.name,
            "location": new_complaint.location,
            "title": new_complaint.title,
            "category": new_complaint.category,
            "priority": new_complaint.priority,
            "status": new_complaint.status,
            "formal_message": new_complaint.formal_message
        },
        "complaint": {
            "id": new_complaint.id,
            "title": new_complaint.title,
            "category": new_complaint.category,
            "priority": new_complaint.priority,
            "status": new_complaint.status,
            "created_at": new_complaint.created_at,
            "original_message": new_complaint.original_message,
            "formal_message": new_complaint.formal_message,
            "audio_path": new_complaint.audio_path
        }
    }


@app.get("/complaints", response_model=List[schemas.ComplaintListResponse])
def get_complaints(db: Session = Depends(get_db)):
    complaints = db.query(models.Complaint).order_by(
        models.Complaint.created_at.desc()).all()
    return complaints


@app.get("/complaints/{id}", response_model=schemas.ComplaintDetailResponse)
def get_complaint_detail(id: int, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(
        models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Сигналът не е намерен")
    return complaint


@app.patch("/complaints/{id}/status")
def update_status(id: int, status_data: schemas.StatusUpdate, db: Session = Depends(get_db)):
    complaint = db.query(models.Complaint).filter(
        models.Complaint.id == id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Сигнал не е намерен")

    valid_statuses = ["New", "Reviewed", "In Progress", "Resolved"]
    if status_data.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Невалиден статус. Позволени: {valid_statuses}"
        )

    complaint.status = status_data.status
    db.commit()
    db.refresh(complaint)

    return {
        "message": "Статусът е обновен успешно",
        "id": complaint.id,
        "new_status": complaint.status
    }
