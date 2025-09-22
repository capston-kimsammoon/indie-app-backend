from pydantic import BaseModel, constr
from typing import List, Optional

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