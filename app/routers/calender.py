from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app.schemas.calendar import (
    CalendarSummaryResponse,
    CalendarPerformanceListResponse,
    CalendarPerformanceItem,
)
from app.crud.calendar import (
    get_calendar_summary_by_month,
    get_performances_by_date,
)

router = APIRouter(prefix="/calendar", tags=["Calendar"])

# [GET] 월별 공연 날짜 마킹 API
@router.get("/summary", response_model=CalendarSummaryResponse)
def read_calendar_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    region: Optional[str] = None,
    db: Session = Depends(get_db),
):
    days = get_calendar_summary_by_month(db, year, month, region)
    return {
        "year": year,
        "month": month,
        "hasPerformanceDates": days
    }

# [GET] 특정 날짜 공연 리스트 API
@router.get("/performance/by-date", response_model=CalendarPerformanceListResponse)
def read_performances_by_date(
    date: date = Query(...),
    region: Optional[str] = None,
    db: Session = Depends(get_db),
):
    performances = get_performances_by_date(db, date, region)

    return {
        "date": str(date),
        "region": region if region else "전체",
        "performances": [
            CalendarPerformanceItem(
                id=p.id,
                title=p.title,
                venue=p.venue.name,
                thumbnail=p.image_url
            ) for p in performances
        ]
    }
