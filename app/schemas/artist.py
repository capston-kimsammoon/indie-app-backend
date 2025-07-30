from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 아티스트 등록 시 사용되는 요청 데이터 모델
class ArtistCreate(BaseModel):
    name: str
    genre: Optional[str] = None
    band_id: Optional[int] = None
    spotify_url: Optional[str] = None
    image_url: Optional[str] = None
    instagram_account: Optional[str] = None

# 아티스트 정보 조회 시 반환되는 응답 모델
class ArtistRead(ArtistCreate):
    id: int

    class Config:
        from_attributes = True

# 아티스트 목록 항목(리스트용)
class ArtistListItem(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    isLiked: bool

# 아티스트 목록 응답 전체 구조
class ArtistListResponse(BaseModel):
    page: int
    totalPages: int
    artists: List[ArtistListItem]

# 공연 미리보기용 구조 (아티스트 상세 페이지에서 사용)
class PerformanceSimple(BaseModel):
    id: int
    title: str
    date: str  # ISO 형식 문자열
    image_url: Optional[str]

# 아티스트 상세 응답 구조
class ArtistDetailResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    spotify_url: Optional[str]
    instagram_account: Optional[str]
    isLiked: bool
    upcomingPerformances: List[PerformanceSimple]
    pastPerformances: List[PerformanceSimple]