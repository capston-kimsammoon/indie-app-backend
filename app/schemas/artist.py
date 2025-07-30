from pydantic import BaseModel
from typing import Optional
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
