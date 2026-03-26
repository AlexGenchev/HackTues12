from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import uvicorn
import shutil
import os

from app.database import engine, SessionLocal, Base
from app import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Box Backend API")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


UPLOAD_DIR = "uploaded_audio"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def process_signal_logic(text: str) -> dict:
    # AI posle

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
        priority = "Low "
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

    formal_message = (
        f"Официално регистрирано оплакване относно: {text}. "
        f"Моля за проверка от съответните органи."
    )

    return {
        "title": title,
        "category": category,
        "priority": priority,
        "formal_message": formal_message
    }


@app.post("/complaints/upload")
def upload_complaint(
    original_text: Optional[str] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    processed_text = original_text
    audio_path = None

    if audio_file:
        file_location = os.path.join(UPLOAD_DIR, audio_file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(audio_file.file, file_object)
        audio_path = file_location

        if not processed_text:
            processed_text = "Текст, генериран от аудио файла."

    if not processed_text:
        raise HTTPException(
            status_code=400,
            detail="Не е предоставен текст или аудио."
        )

    ai_data = process_signal_logic(processed_text)

    new_complaint = models.Complaint(
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

    return {
        "success": True,
        "complaint_id": new_complaint.id,
        "generated_data": {
            "title": new_complaint.title,
            "category": new_complaint.category,
            "priority": new_complaint.priority,
            "status": new_complaint.status,
            "formal_message": new_complaint.formal_message
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


if __name__ == '__main__':
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
