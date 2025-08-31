from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.utils.dependency import get_current_user_optional
from app.schemas.artist import ArtistListResponse, ArtistDetailResponse
from app.crud.artist import get_artist_list, get_artist_detail

router = APIRouter(prefix="/artist", tags=["Artist"])

@router.get("", response_model=ArtistListResponse)
def read_artist_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),   # ✅ 상한 설정
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    try:
        return get_artist_list(db, user.id if user else None, page, size)
    except HTTPException:
        raise
    except Exception as e:
        print("🔥 [ERROR] read_artist_list:", e)
        raise HTTPException(status_code=500, detail="Artist API Error")

@router.get("/{id}", response_model=ArtistDetailResponse)
def read_artist_detail(
    id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    try:
        data = get_artist_detail(db, id, user.id if user else None)
        if not data:
            raise HTTPException(status_code=404, detail="Artist not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        print("🔥 [ERROR] read_artist_detail:", e)
        raise HTTPException(status_code=500, detail="Artist detail API Error")
