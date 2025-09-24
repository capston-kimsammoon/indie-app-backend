# app/schemas/search.py
from typing import Optional, List
from pydantic import BaseModel
from typing import List
from datetime import datetime

# 공연 검색 결과에서 개별 공연 정보 담는 모델
class PerformanceSearchItem(BaseModel):
    id: int
    title: str
    venue: str
    date: datetime
    image_url: Optional[str]

# 공연장 검색 결과에서 개별 공연장 정보 담는 모델
class VenueSearchItem(BaseModel):
    id: int
    name: str
    address: str
    image_url: Optional[str]

# 공연 및 공연장 통합 검색 응답 모델 (공연 탭에서 사용)
class PerformanceSearchResponse(BaseModel):
    page: int
    totalPages: int
    performance: List[PerformanceSearchItem]
    venue: List[VenueSearchItem]


# 아티스트 검색 결과에서 개별 아티스트 정보 담는 모델
class ArtistSearchItem(BaseModel):
    id: int
    name: str
    profile_url: Optional[str]
    isLiked: bool
    isAlarmEnabled: bool

# 아티스트 검색 결과 응답 모델
class ArtistSearchResponse(BaseModel):
    page: int
    totalPages: int
    artists: List[ArtistSearchItem]

# 게시물 검색 결과에서 개별 게시물 정보 담는 모델
class PostSearchItem(BaseModel):
    id: int
    title: str
    author: str
    created_at: datetime

# 게시물 검색 결과 응답 모델
class PostSearchResponse(BaseModel):
    page: int
    totalPages: int
    posts: List[PostSearchItem]