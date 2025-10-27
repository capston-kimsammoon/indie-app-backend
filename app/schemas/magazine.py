# app/schemas/magazine.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class MagazineBlockOut(BaseModel):
    id: int
    order: int
    type: str                         # "text" | "image" | "quote" | "embed" | "divider"
    text: Optional[str] = None
    image_url: Optional[str] = None
    caption: Optional[str] = None
    align: Optional[str] = None       # "left" | "center" | "right"
    meta: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class MagazineListItem(BaseModel):
    id: int
    slug: Optional[str] = None
    title: str
    excerpt: Optional[str] = None
    cover_image_url: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime
    content: Optional[int] = None  # 👈 추가: 공연 ID

    class Config:
        from_attributes = True

class MagazineDetailResponse(BaseModel):
    id: int
    slug: Optional[str] = None
    title: str
    author: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime
    blocks: List[MagazineBlockOut]
    content: Optional[int] = None  # 👈 추가: 공연 ID

    class Config:
        from_attributes = True