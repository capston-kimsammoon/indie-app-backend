from typing import Optional, List
from pydantic import BaseModel

# 사용자가 찜한 아티스트 단건 응답 모델
class UserLikedArtistResponse(BaseModel):
    id: int
    name: str
    image_url: Optional[str]
    isLiked: bool
    isAlarmEnabled: bool

    class Config:
        from_attributes = True

# 찜한 아티스트 목록 응답 모델(페이징 포함)
class UserLikedArtistListResponse(BaseModel):
    page: int
    totalPages: int
    artists: List[UserLikedArtistResponse]
