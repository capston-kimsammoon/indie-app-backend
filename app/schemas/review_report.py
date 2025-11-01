# app/schemas/review_report.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewReportCreate(BaseModel):
    reason: Optional[str] = None

class ReviewReportResponse(BaseModel):
    id: int
    review_id: int
    user_id: int
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
