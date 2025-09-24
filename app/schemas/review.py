from pydantic import BaseModel, constr
from typing import List, Optional
from datetime import datetime

from app.schemas.review_image import ReviewImageItem

__all__ = ["ReviewItem", "ReviewListResponse", "ReviewCreate"]

class ReviewItem(BaseModel):
    id: int
    author: str
    content: str
    created_at: str  # ISO 문자열
    profile_url: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True  

class ReviewListResponse(BaseModel):
    total: int
    items: List[ReviewItem]

    class Config:
        orm_mode = True
        from_attributes = True

class ReviewCreate(BaseModel):
    content: constr(min_length=1, max_length=300)

    class Config:
        from_attributes = True


class ReviewItem(BaseModel):
    id: int
    user_id: int
    venue_id: int
    content: str
    created_at: datetime
    like_count: int
    images: List[ReviewImageItem] = []

    class Config:
        from_attributes = True
