from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.utils.dependency import get_current_user
from app.models.user import User

from app.schemas.performance import PerformanceHomeItem, PerformanceListResponse, RecommendationResponse
import app.crud.performance as crud

router = APIRouter(prefix="/performance/home", tags=["Performance Home"])

# 오늘 예정된 공연
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

# 최근 등록 공연
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

# 티켓 오픈 예정 공연
@router.get("/ticket-opening", response_model=PerformanceListResponse)
def ticket_opening_performances(
    startDate: date = Query(...), endDate: date = Query(...), db: Session = Depends(get_db)
):
    if (endDate - startDate).days > 7:
        raise HTTPException(status_code=400, detail="최대 7일까지만 조회할 수 있어요.")
    performances = crud.get_ticket_opening_performances(db, startDate, endDate)
    return {
        "performances": [
            PerformanceHomeItem(
                id=p.id, title=p.title, date=p.date.isoformat(),
                time=p.time.strftime("%H:%M"), venue=p.venue.name, thumbnail=p.image_url
            ) for p in performances
        ]
    }

# 맞춤 추천 공연
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
