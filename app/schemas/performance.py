from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, time, date

class ArtistSimple(BaseModel):
    id: int
    name: str
    image_url: Optional[str]

class PerformanceDetailResponse(BaseModel):
    id: int
    title: str
    date: datetime
    venueId: int
    venue: str
    artists: List[ArtistSimple]
    price: Optional[str]
    ticket_open_date: Optional[datetime]
    ticket_open_time: Optional[time]
    detailLink: Optional[str]
    isLiked: bool
    isAlarmed: bool

class PerformanceHomeItem(BaseModel):
    id: int
    title: str
    date: str
    time: Optional[str]
    venue: str
    thumbnail: Optional[str]

    class Config:
        from_attributes = True

class PerformanceHomeListResponse(BaseModel):
    performances: List[PerformanceHomeItem]

class RecommendationResponse(BaseModel):
    userId: int
    recommendations: List[PerformanceHomeItem]


class PerformanceListItem(BaseModel):
    id: int
    title: str
    venue: str
    date: str
    thumbnail: Optional[str]


class PerformanceListResponse(BaseModel):
    page: int
    totalPages: int
    performances: List[PerformanceListItem]


class ArtistSummary(BaseModel):
    id: int
    name: str
    image_url: Optional[str]


class PerformanceDetailResponse(BaseModel):
    id: int
    title: str
    date: datetime
    venue: str
    artists: List[ArtistSummary]
    price: str
    ticket_open_date: Optional[date]
    ticket_open_time: Optional[time]
    detailLink: Optional[str]
    isLiked: bool
    isAlarmed: bool
