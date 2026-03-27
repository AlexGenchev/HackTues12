from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from .database import Base


class Complaint(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    original_message = Column(Text, nullable=False)
    # primerno Voda, tok, safety, sustoqnie na ulitsata, bokluk
    formal_message = Column(Text, nullable=False)
    category = Column(String, nullable=False)
    # low, Medium, High# new, reviewed, in progress, resolved
    priority = Column(String, nullable=False)
    status = Column(String, default="New")
    audio_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
