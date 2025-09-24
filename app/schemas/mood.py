# app/schemas/mood.py
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel


# ====== Mood ======
class MoodOut(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# ====== Venue (brief) ======
class VenueBrief(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


# ====== Performance (card for list) ======
class PerformanceCard(BaseModel):
    id: int
    title: str
    image_url: Optional[str] = None
    date: Optional[date] = None
    venue: Optional[VenueBrief] = None

    class Config:
        orm_mode = True


# ====== Response: performances by mood ======
class MoodPerformanceList(BaseModel):
    moodId: int
    performances: List[PerformanceCard]
