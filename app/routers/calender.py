from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from fastapi.responses import JSONResponse

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


@router.get("/summary", response_model=CalendarSummaryResponse)
def read_calendar_summary(
    year: int = Query(...),
    month: int = Query(...),
    region: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
):
    days = get_calendar_summary_by_month(db, year, month, region)
    return {
        "year": year,
        "month": month,
        "hasPerformanceDates": days
    }

@router.get("/performance/by-date", response_model=CalendarPerformanceListResponse)
def read_performances_by_date(
    date: date = Query(...),
    region: Optional[List[str]] = Query(None),
    db: Session = Depends(get_db),
):
    try:
        performances = get_performances_by_date(db, date, region)

        result = [
            CalendarPerformanceItem(
                id=p.id,
                title=p.title,
                venue=p.venue.name if p.venue else "알 수 없음",
                thumbnail=p.image_url
            )
            for p in performances
        ]

        return {
            "date": str(date),
            "region": region if region else [],  # ✅ 여기를 고친 거야 (반드시 List[str]로 반환)
            "performances": result
        }

    except Exception as e:
        print(f"🚨 공연 조회 실패: {e}")
        return {
            "date": str(date),
            "region": region if region else [],  # ✅ 여기도 똑같이
            "performances": []
        }
