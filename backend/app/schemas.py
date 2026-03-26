from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class ComplaintListResponse(BaseModel):
    id: int
    title: str
    category: str
    priority: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ComplaintDetailResponse(ComplaintListResponse):
    original_message: str
    formal_message: str
    audio_path: Optional[str] = None


class StatusUpdate(BaseModel):
    status: str
