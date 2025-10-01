# app/schemas/review.py
from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ---------- 공통 서브 스키마 ----------

class ReviewCreateIn(BaseModel):
    content: str = Field(min_length=1, max_length=300)
    image_urls: list[str] = Field(default_factory=list)  # 공개 버킷 public_url 목록

class ReviewImageOut(BaseModel):
    image_url: Optional[str] = None

    class Config:
        orm_mode = True


class UserBrief(BaseModel):
    id: Optional[int] = None
    nickname: str = "익명"
    profile_url: Optional[str] = None

    class Config:
        orm_mode = True


# /venue/reviews 전용(옵션) – 필요 없으면 서버에서 안 넣어도 OK
class VenueBrief(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    logo_url: Optional[str] = None

    class Config:
        orm_mode = True


# ---------- 단일 리뷰 ----------
class ReviewOut(BaseModel):
    id: int
    content: str
    created_at: Optional[datetime] = None  # ISO 문자열도 자동 파싱됨
    user: Optional[UserBrief] = None

    images: List[ReviewImageOut] = []

    # 좋아요 정보
    like_count: int = 0
    liked_by_me: bool = False

    # 전체 리뷰 목록(/venue/reviews)에서만 내려오는 값
    venue: Optional[VenueBrief] = None

    class Config:
        orm_mode = True


# ---------- 리스트 ----------
class ReviewListOut(BaseModel):
    items: List[ReviewOut] = []
    total: int = 0
    page: int = 1
    size: int = 0

    class Config:
        orm_mode = True
