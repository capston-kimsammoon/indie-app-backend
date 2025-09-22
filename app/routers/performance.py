from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
from datetime import time as dt_time
from pydantic import BaseModel, Field

from app.database import get_db
from app.schemas.performance import (
    PerformanceListResponse,
    PerformanceListItem,
    PerformanceDetailResponse,
    ArtistSummary,
)
from app.crud import performance as performance_crud
from app.models.user import User
from app.models.performance import Performance
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm  # ✅ 추가
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
    dt_val = datetime.combine(performance.date, performance.time or dt_time(0, 0))

    return PerformanceDetailResponse(
        id=performance.id,
        title=performance.title,
        date=dt_val,
        venueId=performance.venue.id,
        venue=performance.venue.name,
        artists=[ArtistSummary(id=a.id, name=a.name, image_url=a.image_url) for a in artists],
        price=f"{performance.price}원" if performance.price is not None else None,
        ticket_open_date=performance.ticket_open_date,
        ticket_open_time=performance.ticket_open_time,
        detailLink=performance.detail_url,
        posterUrl=performance.image_url,
        likeCount=like_count,
        isLiked=is_liked,
        isAlarmed=is_alarmed,
    )


# ====== 공연 생성 → 커밋 직후 알림 발송 ======
class PerformanceCreate(BaseModel):
    title: str
    venue_id: int
    date: date
    time: Optional[dt_time] = None
    price: Optional[int] = None
    ticket_open_date: Optional[date] = None
    ticket_open_time: Optional[dt_time] = None
    detail_url: Optional[str] = None
    image_url: Optional[str] = None
    artist_ids: List[int] = Field(default_factory=list)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_performance(
    body: PerformanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # 1) 공연 생성 (CRUD 내부에서 commit X, flush O 가정)
    perf = performance_crud.create_performance(db, body)

    # 2) 아티스트 매핑
    body_artist_ids = list(set(body.artist_ids or []))
    try:
        if body_artist_ids and hasattr(performance_crud, "set_performance_artists"):
            performance_crud.set_performance_artists(db, perf.id, body_artist_ids)
    except Exception as e:
        print(f"[perf] set_performance_artists error: {e}")

    # 3) 커밋/리프레시로 관계 확정
    db.commit()
    db.refresh(perf)

    # 4) ORM에서 다시 읽어 최종 artist_ids 보정(견고)
    db_artist_ids = [a.id for a in getattr(perf, "artists", [])]
    final_artist_ids = sorted(set(body_artist_ids) | set(db_artist_ids))

    # 5) 새 공연 알림 발송 (실패해도 본 요청은 성공)
    if final_artist_ids:
        try:
            res = notify_artist_followers_on_new_performance(
                db, performance_id=perf.id, artist_ids=final_artist_ids
            )
            print(f"[perf] notify result: {res}")
        except Exception as e:
            print(f"[notify] new_performance_by_artist failed for perf={perf.id}: {e}")

    return {"id": perf.id}


# ====== 예매 오픈 알림 토글 API ======

def _ensure_perf_exists(db: Session, perf_id: int) -> Performance:
    perf = db.query(Performance).filter(Performance.id == perf_id).first()
    if not perf:
        raise HTTPException(status_code=404, detail="Performance not found")
    return perf

@router.get("/{perf_id}/ticket-alarm")
def get_ticket_alarm_status(
    perf_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_perf_exists(db, perf_id)
    exists = db.query(UserPerformanceTicketAlarm).filter_by(
        user_id=user.id, performance_id=perf_id
    ).first() is not None
    return {"isAlarmed": exists}

@router.post("/{perf_id}/ticket-alarm", status_code=status.HTTP_201_CREATED)
def enable_ticket_alarm(
    perf_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_perf_exists(db, perf_id)
    # 중복 삽입 방지
    exists = db.query(UserPerformanceTicketAlarm).filter_by(
        user_id=user.id, performance_id=perf_id
    ).first()
    if not exists:
        db.add(UserPerformanceTicketAlarm(user_id=user.id, performance_id=perf_id))
        db.commit()
    return {"ok": True, "isAlarmed": True}

@router.delete("/{perf_id}/ticket-alarm")
def disable_ticket_alarm(
    perf_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    _ensure_perf_exists(db, perf_id)
    row = db.query(UserPerformanceTicketAlarm).filter_by(
        user_id=user.id, performance_id=perf_id
    ).first()
    if row:
        db.delete(row)
        db.commit()
    return {"ok": True, "isAlarmed": False}


# ====== 디버그 도우미(선택) ======
@router.get("/debug/notify/{perf_id}")
def debug_notify(perf_id: int, db: Session = Depends(get_db)):
    from app.models.performance_artist import PerformanceArtist
    artist_ids = [pa.artist_id for pa in db.query(PerformanceArtist)
                  .filter(PerformanceArtist.performance_id == perf_id).all()]
    if not artist_ids:
        return {"ok": False, "msg": "no artists mapped"}
    res = notify_artist_followers_on_new_performance(db, performance_id=perf_id, artist_ids=artist_ids)
    return {"ok": True, "artist_ids": artist_ids, **res}


@router.get("/debug/pingdb")
def debug_pingdb(db: Session = Depends(get_db)):
    r = db.execute("SELECT DATABASE() AS db, @@port AS port").fetchall()
    return [dict(x._mapping) for x in r]
