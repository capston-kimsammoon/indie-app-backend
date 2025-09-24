from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.venue import Venue
from app.models.performance import Performance
from app.models.review import Review
from app.schemas.venue import VenueListResponse, VenueListItem, VenueDetailResponse, VenuePerformanceItem
from app.schemas.review import ReviewListResponse, ReviewItem
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
    venues = query.offset(skip).limit(size).all()

    result = [
        VenueListItem(id=v.id, name=v.name,        address=v.address,         region=v.region, image_url=v.image_url)
        for v in venues
    ]

    total_pages = (total + size - 1) // size
    return VenueListResponse(page=page, totalPages=total_pages, venue=result)



# 🎯 공연장 상세 정보 조회
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

    return VenueDetailResponse(
        id=venue.id,
        name=venue.name,
        image_url=venue.image_url,
        instagram_account=venue.instagram_account,
        address=venue.address,
        latitude=venue.latitude,
        longitude=venue.longitude,
        upcomingPerformance=upcoming_performances
    )


@router.get("/{venue_id}/review", response_model=ReviewListResponse)
def list_venue_reviews(
    venue_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    # 존재 체크(선택): 공연장 없으면 404
    venue_exists = db.query(Venue.id).filter(Venue.id == venue_id).first()
    if not venue_exists:
        raise HTTPException(status_code=404, detail="Venue not found")

    base_q = (
        db.query(Review)
        .filter(Review.venue_id == venue_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
    )

    total = base_q.count()
    rows = (
        base_q.options(joinedload(Review.user))
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )

    items = []
    for r in rows:
        author = "익명"
        # User.nickname(혹은 name) 사용 — 프로젝트 스키마에 맞춰 필드명 조정
        if getattr(r, "user", None):
            author = getattr(r.user, "nickname", None) or getattr(r.user, "name", None) or "익명"

        items.append(
            ReviewItem(
                id=r.id,
                author=author,
                content=r.content,
                created_at=r.created_at.isoformat() if r.created_at else "",
            )
        )

    return ReviewListResponse(total=total, items=items)