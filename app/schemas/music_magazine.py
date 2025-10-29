from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class MusicMagazineBlockOut(BaseModel):
    id: int
    order: int                       # 모델의 display_order를 라우터에서 매핑
    type: str                        # "text" | "image" | "divider" | "cta"
    semititle: Optional[str] = None  # 소제목
    text: Optional[str] = None
    image_url: Optional[str] = None
    artist_id: Optional[int] = None

    class Config:
        from_attributes = True

class MusicMagazineListItem(BaseModel):
    id: int
    slug: Optional[str] = None
    title: str
    excerpt: Optional[str] = None
    cover_image_url: Optional[str] = None
    author: Optional[str] = None
    created_at: datetime
    content: Optional[int] = None

    class Config:
        from_attributes = True

class MusicMagazineDetailResponse(BaseModel):
    id: int
    slug: Optional[str] = None
    title: str
    author: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: datetime
    blocks: List[MusicMagazineBlockOut]
    content: Optional[int] = None

    class Config:
        from_attributes = True
