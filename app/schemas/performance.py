# app/schemas/performance.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, time, date

class ArtistSimple(BaseModel):
    id: int
    name: str
    image_url: Optional[str]

class PerformanceHomeItem(BaseModel):
    id: int
    title: str
    date: str
    time: Optional[str]
    venue: str
    thumbnail: Optional[str]

    class Config:
        from_attributes = True

class PerformanceListItem(BaseModel):
    id: int
    title: str
    venue: str
    date: str
    time: Optional[str] = None
    thumbnail: Optional[str]

class PerformanceListResponse(BaseModel):
    page: Optional[int] = None
    totalPages: Optional[int] = None
    performances: List[PerformanceListItem]

class RecommendationResponse(BaseModel):
    userId: int
    recommendations: List[PerformanceHomeItem]

class ArtistSummary(BaseModel):
    id: int
    name: str
    image_url: Optional[str]

class PerformanceDetailResponse(BaseModel):
    id: int
    title: str
    date: datetime
    venueId: int
    venue: str
    artists: List[ArtistSummary]
    price: str
    ticket_open_date: Optional[date]
    ticket_open_time: Optional[time]
    shortcode: Optional[str]
    detailLink: Optional[str]
    posterUrl: Optional[str]
    likeCount: int
    isLiked: bool
    isAlarmed: bool

# ✅ 새로 추가된 응답 스키마 (티켓 오픈용)
class PerformanceTicketOpenItem(BaseModel):
    id: int
    title: str
    date: str
    time: Optional[str]
    venue: str
    thumbnail: Optional[str]
    ticket_open_date: Optional[date] = None

    class Config:
        from_attributes = True

class PerformanceTicketOpenListResponse(BaseModel):
    page: Optional[int] = None
    totalPages: Optional[int] = None
    performances: List[PerformanceTicketOpenItem]
