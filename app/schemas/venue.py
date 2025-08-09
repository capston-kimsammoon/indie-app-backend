# app/schemas/venue.py
from pydantic import BaseModel
from typing import List, Optional

# 공연장 목록의 개별 항목(간략 정보)
class VenueListItem(BaseModel):
    id: int
    name: str
    region: str
    address: str  
    image_url: Optional[str]

    class Config:  
        orm_mode = True

# 공연장 목록 전체 응답(페이징 포함)
class VenueListResponse(BaseModel):
    page: int
    totalPages: int
    venue: List[VenueListItem]

# 공연장 상세 페이지에서 예정 공연 리스트에 사용되는 공연 항목
class VenuePerformanceItem(BaseModel):
    id: int
    title: str
    date: str  # ISO 포맷
    time: Optional[str]  # ✅ 조수아 추가 (HH:MM 포맷)
    image_url: Optional[str]

# 공연장 상세 정보 + 예정 공연 응답 모델
class VenueDetailResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    instagram_account: str
    address: str
    latitude: float
    longitude: float
    upcomingPerformance: List[VenuePerformanceItem]
