# schemas/stamp.py에 추가해야 할 스키마들

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# ✅ 사용 가능한 스탬프 응답 (프론트엔드에서 필요한 정보)
class AvailableStampResponse(BaseModel):
    id: int
    performance_id: int
    posterUrl: Optional[str] = None
    venueImageUrl: Optional[str] = None
    place: str
    title: str
    date: datetime
    is_collected: bool
    
    class Config:
        from_attributes = True

# ✅ 스탬프 수집 요청
class StampCollectRequest(BaseModel):
    stampId: int  # performance_id

# ✅ 기존 StampResponse에 추가 필드가 필요할 수 있음
class StampResponse(BaseModel):
    id: int
    user_id: int
    performance_id: int
    created_at: datetime
    # ✅ 관계 데이터 (필요시)
    performance: Optional[dict] = None  # Performance 정보
    
    class Config:
        from_attributes = True