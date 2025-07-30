from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.models.performance import Performance
from app.models.venue import Venue

router = APIRouter(prefix="/calendar", tags=["Calendar"])

# 캘린더 1. 월별 공연 날짜 마킹
@router.get("/summary")
def get_calendar_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    region: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    월별 공연 날짜 마킹
    """
    query = db.query(Performance.date)

    query = query.filter(
        Performance.date >= date(year, month, 1),
        Performance.date < date(year, month + 1 if month < 12 else 1, 1 if month < 12 else 9999),
    )

    if region:
        query = query.join(Performance.venue).filter(Venue.region == region)

    result = query.all()
    days = sorted({d.date.day for d in result})

    return {
        "year": year,
        "month": month,
        "hasPerformanceDates": days
    }

# 캘린더 2. 날짜별 공연 리스트
@router.get("/performance/by-date")
def get_performances_by_date(
    date: date = Query(...),
    region: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    날짜별 공연 리스트 조회
    """
    query = db.query(Performance).filter(Performance.date == date)

    if region:
        query = query.join(Performance.venue).filter(Venue.region == region)

    performances = query.all()

    return {
        "date": str(date),
        "region": region if region else "전체",
        "performances": [
            {
                "id": p.id,
                "title": p.title,
                "venue": p.venue.name,
                "thumbnail": p.image_url
            }
            for p in performances
        ]
    }