from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Union, List, Optional
from datetime import date
from sqlalchemy import or_

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

def parse_region(region: Union[List[str], str, None]) -> List[str]:
    region_list = []
    if region:
        if isinstance(region, str):
            region_list = [r.strip() for r in region.split(",") if r.strip()]
        elif isinstance(region, list):
            for r in region:
                for p in r.split(","):
                    p = p.strip()
                    if p:
                        region_list.append(p)
    return region_list

# [GET] 월별 공연 날짜 마킹 API
@router.get("/summary", response_model=CalendarSummaryResponse)
def read_calendar_summary(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    region: Union[List[str], str, None] = Query(None, description="지역 필터"),
    db: Session = Depends(get_db),
):
    region_list = parse_region(region)

    # '전체' 포함 시 전체 조회 처리
    if not region_list or "전체" in region_list:
        region_list = []

    days = get_calendar_summary_by_month(db, year, month, region_list)
    return {
        "year": year,
        "month": month,
        "hasPerformanceDates": days
    }

# [GET] 특정 날짜 공연 리스트 API
@router.get("/performance/by-date", response_model=CalendarPerformanceListResponse)
def read_performances_by_date(
    date: date = Query(...),
    region: Union[List[str], str, None] = Query(None, description="지역 필터"),
    db: Session = Depends(get_db),
):
    region_list = parse_region(region)

    if not region_list or "전체" in region_list:
        region_list = []

    performances = get_performances_by_date(db, date, region_list)

    return {
        "date": str(date),
        "region": ", ".join(region_list) if region_list else "전체",
        "performances": [
            CalendarPerformanceItem(
                id=p.id,
                title=p.title,
                venue=p.venue.name,
                thumbnail=p.image_url
            ) for p in performances
        ]
    }
