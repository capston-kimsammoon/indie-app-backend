# app/routers/performance.py
from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date, time
from pydantic import BaseModel

from app.database import get_db
from app.schemas.performance import (
    PerformanceListResponse,
    PerformanceListItem,
    PerformanceDetailResponse,
    ArtistSummary,
)
from app.crud import performance as performance_crud
from app.models.user import User
from app.utils.dependency import get_current_user_optional, get_current_user
from app.services.notify import notify_artist_followers_on_new_performance

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("", response_model=PerformanceListResponse)
def get_performance_list(
    region: Optional[List[str]] = Query(None),
    sort: str = Query("date", pattern="^(date|created_at|likes)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    performances, total = performance_crud.get_performances(db, region, sort, page, size)
    return PerformanceListResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        performances=[
            PerformanceListItem(
                id=p.id,
                title=p.title,
                venue=p.venue.name,
                date=p.date.isoformat(),
                time=p.time.strftime("%H:%M") if p.time else None,
                thumbnail=p.image_url,
            )
            for p in performances
        ],
    )


@router.get("/{id}", response_model=PerformanceDetailResponse)
def get_performance_detail(
    id: int,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    performance = performance_crud.get_performance_detail(db, id)
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")

    artists = performance_crud.get_performance_artists(db, id)

    is_liked = is_alarmed = False
    if user:
        is_liked = performance_crud.is_user_liked_performance(db, user.id, id)
        is_alarmed = performance_crud.is_user_alarmed_performance(db, user.id, id)

    like_count = performance_crud.get_performance_like_count(db, id)

    return PerformanceDetailResponse(
        id=performance.id,
        title=performance.title,
        date=datetime.combine(performance.date, performance.time),
        venueId=performance.venue.id,
        venue=performance.venue.name,
        artists=[ArtistSummary(id=a.id, name=a.name, image_url=a.image_url) for a in artists],
        price=f"{performance.price}원",
        ticket_open_date=performance.ticket_open_date,
        ticket_open_time=performance.ticket_open_time,
        detailLink=performance.detail_url,
        posterUrl=performance.image_url,
        likeCount=like_count,
        isLiked=is_liked,
        isAlarmed=is_alarmed,
    )


# ====== ✅ 공연 생성(POST) — 커밋 직후 팔로워에게 새 공연 알림 생성 ======

class PerformanceCreate(BaseModel):
    title: str
    venue_id: int
    date: date
    time: Optional[time] = None
    price: Optional[int] = None
    ticket_open_date: Optional[date] = None
    ticket_open_time: Optional[time] = None
    detail_url: Optional[str] = None
    image_url: Optional[str] = None
    artist_ids: List[int] = []  # 이 공연에 연결할 아티스트 id 목록


@router.post("", status_code=status.HTTP_201_CREATED)
def create_performance(
    body: PerformanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),  # 인증 필요 시
):
    # 1) 공연 생성 (프로젝트 CRUD에 맞춰 호출)
    perf = performance_crud.create_performance(db, body)

    # 2) 아티스트 매핑
    artist_ids = body.artist_ids or []
    try:
        if artist_ids:
            performance_crud.set_performance_artists(db, perf.id, artist_ids)
    except AttributeError:
        # 프로젝트에 set_performance_artists가 없다면, 모델 관계를 직접 추가하는 로직을 쓰세요.
        pass

    # 3) 먼저 커밋해 id/관계 확정
    db.commit()
    db.refresh(perf)

    # body에 없으면 관계에서 추출
    if not artist_ids:
        try:
            artist_ids = [rel.artist_id for rel in getattr(perf, "artists", [])]
        except Exception:
            artist_ids = []

    # 4) ✅ 새 공연 알림 (아티스트 팔로워 대상)
    notify_artist_followers_on_new_performance(
        db, performance_id=perf.id, artist_ids=artist_ids
    )

    return {"id": perf.id}
