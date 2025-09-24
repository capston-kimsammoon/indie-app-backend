from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 공연장 응답용
class VenueResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

# 공연 정보 응답용
class PerformanceResponse(BaseModel):
    id: int
    title: str
    date: datetime
    image_url: Optional[str] = None
    venue: Optional[VenueResponse] = None  # ✅ venue 객체 포함

    class Config:
        from_attributes = True

# 사용 가능한 스탬프 응답 (프론트에서 필요한 정보)
class AvailableStampResponse(BaseModel):
    id: int
    performance_id: int
    posterUrl: Optional[str] = None
    venueImageUrl: Optional[str] = None
    venue: str
    title: str
    date: datetime
    is_collected: bool
    
    class Config:
        from_attributes = True

# 스탬프 수집 요청
class StampCollectRequest(BaseModel):
    stampId: int  # performance_id

# 수집한 스탬프 응답
class StampResponse(BaseModel):
    id: int
    user_id: int
    performance_id: int
    created_at: datetime
    performance: Optional[PerformanceResponse] = None  # nested 관계
    
    class Config:
        from_attributes = True
