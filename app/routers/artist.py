from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List, Any
from datetime import datetime

from app.database import get_db
from app.models.artist import Artist
from app.models.performance import Performance
from app.models.performance_artist import PerformanceArtist
from app.models.user_favorite_artist import UserFavoriteArtist

router = APIRouter(prefix="/artist", tags=["Artist"])

# 아티스트 1. 아티스트 목록 조회
@router.get("")
def get_artist_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    user: Optional[Any] = None
):
    query = db.query(Artist)

    total = query.count()
    offset = (page - 1) * size
    artists = query.offset(offset).limit(size).all()
    total_pages = (total + size - 1) // size

    result = []
    for artist in artists:
        is_liked = False
        if user:
            is_liked = db.query(UserFavoriteArtist).filter_by(user_id=user.id, artist_id=artist.id).first() is not None
        result.append({
            "id": artist.id,
            "name": artist.name,
            "image_url": artist.image_url,
            "isLiked": is_liked
        })

    return {
        "page": page,
        "totalPages": total_pages,
        "artists": result
    }

# 아티스트 2. 아티스트 상세 조회
@router.get("/{id}")
def get_artist_detail(
    id: int,
    db: Session = Depends(get_db),
    user: Optional[Any] = None
):
    artist = db.query(Artist).filter_by(id=id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    is_liked = False
    if user:
        is_liked = db.query(UserFavoriteArtist).filter_by(user_id=user.id, artist_id=id).first() is not None

    now = datetime.now()
    performance_ids = db.query(PerformanceArtist.performance_id).filter_by(artist_id=id).subquery()
    performances = db.query(Performance).filter(Performance.id.in_(performance_ids)).all()

    upcoming = []
    past = []

    for p in performances:
        perf_data = {
            "id": p.id,
            "title": p.title,
            "date": f"{p.date}T{p.time.strftime('%H:%M')}",
            "image_url": p.image_url
        }
        if datetime.combine(p.date, p.time) >= now:
            upcoming.append(perf_data)
        else:
            past.append(perf_data)

    return {
        "id": artist.id,
        "name": artist.name,
        "image_url": artist.image_url,
        "spotify_url": artist.spotify_url,
        "instagram_account": artist.instagram_account,
        "isLiked": is_liked,
        "upcomingPerformances": upcoming,
        "pastPerformances": past
    }
