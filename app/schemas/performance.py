from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, time

class ArtistSimple(BaseModel):
    id: int
    name: str
    image_url: Optional[str]

class PerformanceDetailResponse(BaseModel):
    id: int
    title: str
    date: datetime
    venue: str
    artists: List[ArtistSimple]
    price: Optional[str]
    ticket_open_date: Optional[datetime]
    ticket_open_time: Optional[time]
    detailLink: Optional[str]
    isLiked: bool
    isAlarmed: bool
