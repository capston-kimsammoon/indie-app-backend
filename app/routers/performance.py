from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Any, Union
from datetime import datetime

from app.database import get_db
from app.schemas.performance import (
    PerformanceListResponse,
    PerformanceListItem,
    PerformanceDetailResponse,
    ArtistSummary,
)
from app.crud import performance as performance_crud
from app.models.user import User
from app.utils.dependency import get_current_user_optional

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("", response_model=PerformanceListResponse)
def get_performance_list(
    region: Union[List[str], str, None] = Query(None, description="지역 필터"),
    sort: str = Query("date", pattern="^(date|created_at|likes)$"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
):
    # 1. 문자열 또는 리스트로 들어온 region 파싱
    region_list = []
    if region:
        if isinstance(region, str):
            region_list = [r.strip().lower() for r in region.split(",") if r.strip()]
        elif isinstance(region, list):
            for r in region:
                for p in r.split(","):
                    p = p.strip().lower()
                    if p:
                        region_list.append(p)

    # 2. crud로 전달
    performances, total = performance_crud.get_performances(
        db, region_list, sort, page, size
    )

    return PerformanceListResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        performances=[
            PerformanceListItem(
                id=p.id,
                title=p.title,
                venue=p.venue.name,
                date=f"{p.date}T{p.time}",
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

    return PerformanceDetailResponse(
        id=performance.id,
        title=performance.title,
        date=datetime.combine(performance.date, performance.time),
        venueId=performance.venue.id,
        venue=performance.venue.name,
        artists=[
            ArtistSummary(id=a.id, name=a.name, image_url=a.image_url)
            for a in artists
        ],
        price=f"{performance.price}원",
        ticket_open_date=performance.ticket_open_date,
        ticket_open_time=performance.ticket_open_time,
        detailLink=performance.detail_url,
        isLiked=is_liked,
        isAlarmed=is_alarmed,
    )
