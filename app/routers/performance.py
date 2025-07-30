from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, List, Optional
from datetime import datetime

from app.database import get_db
from app.models.performance import Performance
from app.models.performance_artist import PerformanceArtist
from app.models.artist import Artist
from app.models.venue import Venue
from app.models.user import User
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.models.user_favorite_performance import UserFavoritePerformance
from app.schemas.performance import PerformanceDetailResponse


router = APIRouter(tags=["Performance"])

# 공연 1. 공연 목록 조회
@router.get("/performance")
def get_performance_list(
    region: Optional[List[str]] = Query(None),
    sort: str = Query("date", regex="^(date|created_at|likes)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    query = db.query(Performance).join(Venue)

    # 지역 필터링 (중복 선택 가능)
    if region and "전체" not in region:
        query = query.filter(Venue.region.in_(region))

    if sort == "date":
        query = query.order_by(Performance.date.asc())
    elif sort == "created_at":
        query = query.order_by(Performance.created_at.desc())
    elif sort == "likes":
        # 찜 수 기준 정렬 (LEFT OUTER JOIN + GROUP BY)
        query = (
            query.outerjoin(UserFavoritePerformance, UserFavoritePerformance.c.performance_id == Performance.id)
            .group_by(Performance.id, Venue.id)
            .order_by(func.count(UserFavoritePerformance.c.user_id).desc())
        )

    total = query.count()

    offset = (page - 1) * size
    performances = query.offset(offset).limit(size).all()

    total_pages = (total + size - 1) // size

    return {
        "page": page,
        "totalPages": total_pages,
        "performances": [
            {
                "id": p.id,
                "title": p.title,
                "venue": p.venue.name,
                "date": f"{p.date}T{p.time.strftime('%H:%M')}",
                "thumbnail": p.image_url,
            }
            for p in performances
        ],
    }

# 공연 2. 공연 상세 정보 조회
@router.get("/performance/{id}", response_model=PerformanceDetailResponse)
def get_performance_detail(
    id: int,
    db: Session = Depends(get_db),
    user: Optional[Any] = None, 
):
    performance = db.query(Performance).filter(Performance.id == id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")

    artists = (
        db.query(Artist)
        .join(PerformanceArtist, PerformanceArtist.artist_id == Artist.id)
        .filter(PerformanceArtist.performance_id == id)
        .all()
    )

    is_liked = False
    is_alarmed = False
    if user:
        is_liked = db.query(UserFavoritePerformance).filter_by(user_id=user.id, performance_id=id).first() is not None
        is_alarmed = db.query(UserPerformanceTicketAlarm).filter_by(user_id=user.id, performance_id=id).first() is not None

    datetime_combined = datetime.combine(performance.date, performance.time)

    return {
        "id": performance.id,
        "title": performance.title,
        "date": datetime_combined,
        "venue": performance.venue.name,
        "artists": [{"id": a.id, "name": a.name, "image_url": a.image_url} for a in artists],
        "price": f"{performance.price}원", 
        "ticket_open_date": performance.ticket_open_date,
        "ticket_open_time": performance.ticket_open_time,
        "detailLink": performance.detail_url,  
        "isLiked": is_liked,
        "isAlarmed": is_alarmed
    }
