from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# 사용자가 찜한 공연 단건 응답 모델
class UserLikedPerformanceResponse(BaseModel):
    id: int
    title: str
    venue: str
    date: datetime
    image_url: Optional[str]
    isLiked: bool

    class Config:
        from_attributes = True

# 찜한 공연 목록 응답 모델(페이징 포함)
class UserLikedPerformanceListResponse(BaseModel):
    page: int
    totalPages: int
    performances: List[UserLikedPerformanceResponse]
