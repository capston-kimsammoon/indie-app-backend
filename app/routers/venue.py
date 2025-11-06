# from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.venue import Venue
from app.models.performance import Performance
from app.models.review import Review
from app.schemas.venue import VenueListResponse, VenueListItem, VenueDetailResponse, VenuePerformanceItem
from sqlalchemy import or_, asc, text

from app.crud import venue as venue_crud
from typing import Optional, List, Union
from sqlalchemy import or_

router = APIRouter(
    prefix="/venue",
    tags=["Venue"]
)
#공욘장리스틎회
@router.get("", response_model=VenueListResponse)
def get_venue_list(
    region: Union[List[str], str, None] = Query(None, description="지역 필터"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size
    query = db.query(Venue)

    # ✅ region을 항상 배열로 변환 + 내부 콤마도 분리
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

    # ✅ Debug 로그로 region 실제 값 확인
    print("🎯 [DEBUG] 최종 region 리스트:", region_list)

    # ✅ OR 조건으로 부분 일치 검색
    if region_list and "전체" not in region_list:
        conditions = [Venue.region.ilike(f"%{r}%") for r in region_list]
        query = query.filter(or_(*conditions))

    total = query.count()

    # ✅ ㄱ-ㄴ-ㄷ(한글) 정렬 + tie-breaker로 id
    #   - MySQL 8 권장 콜레이션: utf8mb4_0900_ai_ci
    #   - 프로젝트 콜레이션이 다르면 해당 값으로 바꿔도 됨
    query = query.order_by(
        text("CONVERT(name USING utf8mb4) COLLATE utf8mb4_0900_ai_ci ASC"),
        asc(Venue.id)
    )

    # 페이지네이션
    venues = query.offset(skip).limit(size).all()

    result = [
        VenueListItem(id=v.id, name=v.name,        address=v.address,         region=v.region, image_url=v.image_url)
        for v in venues
    ]

    total_pages = (total + size - 1) // size
    return VenueListResponse(page=page, totalPages=total_pages, venue=result)



@router.get("/{venue_id}", response_model=VenueDetailResponse)
def get_venue_detail(
    venue_id: int,
    db: Session = Depends(get_db)
):
    venue = venue_crud.get_venue_by_id(db, venue_id)
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    upcoming = venue_crud.get_upcoming_performances_by_venue(db, venue_id)
    upcoming_performances = [
        VenuePerformanceItem(
            id=p.id,
            title=p.title,
            date=f"{p.date}T{p.time}",
            image_url=p.image_url
        ) for p in upcoming
    ]

    past = venue_crud.get_past_performances_by_venue(db, venue_id)

    past_performances = [
    VenuePerformanceItem(
        id=p.id,
        title=p.title,
        date=f"{p.date}T{str(p.time)[:5] if p.time else '00:00'}",
        image_url=p.image_url
    )
    for p in past
    ]

    #print(f"[VENUE {venue_id}] upcoming={len(upcoming_performances)} past={len(past_performances)}")
    return VenueDetailResponse(
        id=venue.id,
        name=venue.name,
        description=venue.description,
        image_url=venue.image_url,
        instagram_account=venue.instagram_account,
        address=venue.address,
        latitude=venue.latitude,
        longitude=venue.longitude,
        upcomingPerformance=upcoming_performances,
        pastPerformance=past_performances
    )
