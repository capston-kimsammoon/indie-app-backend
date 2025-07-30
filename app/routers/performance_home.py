# routers/performance_home.py
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from datetime import date, datetime
from app.database import SessionLocal
from app.models.performance import Performance
from app.models.venue import Venue
from app.models.user import User
from app.models.user_favorite_performance import UserFavoritePerformance
from app.utils.dependency import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 홈 1. 오늘 예정된 공연
@router.get("/today")
def get_today_performances(db: Session = Depends(get_db)):
    today = date.today()

    performances = (
        db.query(Performance)
        .join(Venue, Performance.venue_id == Venue.id)
        .filter(Performance.date == today)
        .all()
    )

    results = []
    for p in performances:
        results.append({
            "id": p.id,
            "title": p.title,
            "date": p.date.isoformat(),  
            "time": p.time.strftime("%H:%M"), 
            "venue": p.venue.name,
            "thumbnail": p.image_url
        })

    return {"performances": results}


# 홈 2. NEW 업로드 공연
@router.get("/recent")
def get_recent_performances(
    limit: int = Query(6, ge=3, le=6), 
    db: Session = Depends(get_db)
):
    """
    최근 등록된 공연 (3~6개)
    - limit: 가져올 개수 (기본 6, 최소 3, 최대 6)
    """
    performances = (
        db.query(Performance)
        .join(Venue, Performance.venue_id == Venue.id)
        .order_by(Performance.created_at.desc())
        .limit(limit)
        .all()
    )

    results = []
    for p in performances:
        results.append({
            "id": p.id,
            "title": p.title,
            "date": p.date.isoformat(),
            "time": p.time.strftime("%H:%M"),
            "venue": p.venue.name,
            "thumbnail": p.image_url
        })

    return {"performances": results}

# 홈 3. 티켓 오픈 예정 공연
@router.get("/ticket-opening")
def get_ticket_opening_performances(
    startDate: date = Query(..., description="형식: YYYY-MM-DD"),
    endDate: date = Query(..., description="형식: YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    티켓 오픈 예정 공연
    - startDate ~ endDate 사이의 ticket_open_date 범위로 조회 (최대 7일 차이)
    """

    if (endDate - startDate).days > 7:
        raise HTTPException(status_code=400, detail="최대 7일까지만 조회할 수 있어요.")

    performances = (
        db.query(Performance)
        .join(Venue, Performance.venue_id == Venue.id)
        .filter(Performance.ticket_open_date >= startDate)
        .filter(Performance.ticket_open_date <= endDate)
        .all()
    )

    results = [
        {
            "id": p.id,
            "title": p.title,
            "date": p.date.isoformat(),
            "time": p.time.strftime("%H:%M"),
            "venue": p.venue.name,
            "thumbnail": p.image_url
        }
        for p in performances
    ]

    return {"performances": results}

# 홈 4. 맞춤 추천 공연
@router.get("/recommendation")
def get_recommendation_performances(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    user_id = current_user.id

    liked_perf_ids_subq = (
        db.query(UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id == user_id)
        .subquery()
    )

    other_users_subq = (
        db.query(UserFavoritePerformance.user_id)
        .filter(UserFavoritePerformance.performance_id.in_(liked_perf_ids_subq))
        .filter(UserFavoritePerformance.user_id != user_id)
        .distinct()
        .subquery()
    )

    performances = (
        db.query(Performance)
        .join(UserFavoritePerformance, Performance.id == UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id.in_(other_users_subq))
        .filter(~Performance.id.in_(liked_perf_ids_subq))
        .order_by(func.rand())
        .limit(6)
        .all()
    )

    results = [
        {
            "id": p.id,
            "title": p.title,
            "date": p.date.isoformat(),
            "venue": p.venue.name,
            "thumbnail": p.image_url,
        }
        for p in performances
    ]

    return {
        "userId": user_id,
        "recommendations": results
    }