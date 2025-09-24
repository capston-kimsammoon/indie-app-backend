# app/schemas/review_like.py
from pydantic import BaseModel
from datetime import datetime

class ReviewLikeToggleResponse(BaseModel):
    review_id: int
    like_count: int
    liked: bool  # 현재 사용자 기준으로 좋아요 상태

class ReviewLikeItem(BaseModel):
    id: int
    review_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
