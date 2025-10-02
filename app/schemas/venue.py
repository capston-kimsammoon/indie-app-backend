from pydantic import BaseModel
from typing import List, Optional

# 공연장 목록의 개별 항목(간략 정보)
class VenueListItem(BaseModel):
    id: int
    name: str
    region: str
    address: str
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

# 공연장 목록 전체 응답(페이징 포함)
class VenueListResponse(BaseModel):
    page: int
    totalPages: int
    venue: List[VenueListItem]

    class Config:
        orm_mode = True

# 공연장 상세 페이지에서 예정 공연 리스트에 사용되는 공연 항목
class VenuePerformanceItem(BaseModel):
    id: int
    title: str
    date: str              # ISO 포맷
    time: Optional[str] = None     # HH:MM
    image_url: Optional[str] = None

    class Config:
        orm_mode = True

# 공연장 상세 정보 + 예정 공연 응답 모델
class VenueDetailResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None
    instagram_account: Optional[str] = None   # ← Optional
    address: str
    latitude: float
    longitude: float
    upcomingPerformance: List[VenuePerformanceItem] = []  
    pastPerformance: List[VenuePerformanceItem] = []
    
    class Config:
        orm_mode = True
