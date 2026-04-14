from datetime import datetime, timezone
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from backend.database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    audio_filename = Column(String, nullable=True)
    transcribed_text = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    location_mentioned = Column(String, nullable=True)
    urgency = Column(String, nullable=False)
    formal_letter = Column(Text, nullable=False)
    sent_to_email = Column(String, nullable=False)
    email_sent_successfully = Column(Boolean, nullable=False, default=False)
