from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.dependency import get_current_user_optional
from app.schemas.artist import ArtistListResponse, ArtistDetailResponse
from app.crud.artist import get_artist_list, get_artist_detail

router = APIRouter(prefix="/artist", tags=["Artist"])

# [GET] 아티스트 목록 조회 API
# 페이징 처리, 찜 여부 포함
@router.get("", response_model=ArtistListResponse)
def read_artist_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    return get_artist_list(db, user.id if user else None, page, size)

# [GET] 아티스트 상세 조회 API
# 기본 정보 + 예정/지난 공연 + 찜 여부 포함
@router.get("/{id}", response_model=ArtistDetailResponse)
def read_artist_detail(
    id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional)
):
    artist = get_artist_detail(db, id, user.id if user else None)
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")
    return artist
