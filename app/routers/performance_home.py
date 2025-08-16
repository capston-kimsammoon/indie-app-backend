# app/router/performance/home.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.utils.dependency import get_current_user
from app.models.user import User

from app.schemas.performance import (
    PerformanceHomeItem,
    PerformanceListResponse,
    RecommendationResponse,
    PerformanceTicketOpenItem,              # ✅ 추가
    PerformanceTicketOpenListResponse       # ✅ 추가
)

import app.crud.performance as crud

router = APIRouter(prefix="/performance/home", tags=["Performance Home"])

@router.get("/today", response_model=PerformanceListResponse)
def today_performances(db: Session = Depends(get_db)):
    performances = crud.get_today_performances(db)
    return {
        "performances": [
            PerformanceHomeItem(
                id=p.id, title=p.title, date=p.date.isoformat(),
                time=p.time.strftime("%H:%M"), venue=p.venue.name, thumbnail=p.image_url
            ) for p in performances
        ]
    }

@router.get("/recent", response_model=PerformanceListResponse)
def recent_performances(limit: int = Query(6, ge=3, le=6), db: Session = Depends(get_db)):
    performances = crud.get_recent_performances(db, limit)
    return {
        "performances": [
            PerformanceHomeItem(
                id=p.id, title=p.title, date=p.date.isoformat(),
                time=p.time.strftime("%H:%M"), venue=p.venue.name, thumbnail=p.image_url
            ) for p in performances
        ]
    }

# ✅ 수정된 티켓 오픈 예정 공연 라우터
@router.get("/ticket-opening", response_model=PerformanceTicketOpenListResponse)
def ticket_opening_performances(
    startDate: date = Query(...), endDate: date = Query(...), db: Session = Depends(get_db)
):
    if (endDate - startDate).days > 7:
        raise HTTPException(status_code=400, detail="최대 7일까지만 조회할 수 있어요.")
    performances = crud.get_ticket_opening_performances(db, startDate, endDate)
    return {
        "performances": [
            PerformanceTicketOpenItem(
                id=p.id,
                title=p.title,
                date=p.date.isoformat(),
                # ⬇️ 공연 시간이 아니라 "티켓 오픈 시간"을 내려줍니다.
                time=(p.ticket_open_time.strftime("%H:%M") if p.ticket_open_time else None),
                venue=p.venue.name,
                thumbnail=p.image_url,
                ticket_open_date=p.ticket_open_date  # ← date 타입이면 자동 ISO('YYYY-MM-DD')
            ) for p in performances
        ]
    }

@router.get("/recommendation", response_model=RecommendationResponse)
def recommendation_performances(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    performances = crud.get_recommendation_performances(db, current_user.id)
    return {
        "userId": current_user.id,
        "recommendations": [
            PerformanceHomeItem(
                id=p.id, title=p.title, date=p.date.isoformat(),
                time=p.time.strftime("%H:%M"), venue=p.venue.name, thumbnail=p.image_url
            ) for p in performances
        ]
    }
