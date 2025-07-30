from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.venue import Venue
from app.models.performance import Performance
from app.schemas.venue import VenueListResponse, VenueListItem, VenueDetailResponse, VenuePerformanceItem
from app.crud import venue as venue_crud

router = APIRouter(
    prefix="/venue",
    tags=["Venue"]
)

# 공연장 목록 조회
@router.get("", response_model=VenueListResponse)
def get_venue_list(
    region: str = Query(..., description="지역 필터"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    if region == "전체":
        query = db.query(Venue)
    else:
        query = db.query(Venue).filter(Venue.region == region)

    total = query.count()
    venues = query.offset(skip).limit(size).all()

    result = [
        VenueListItem(
            id=v.id,
            name=v.name,
            region=v.region,
            image_url=v.image_url
        ) for v in venues
    ]

    total_pages = (total + size - 1) // size
    return VenueListResponse(page=page, totalPages=total_pages, venue=result)

# 공연장 상세 정보 조회
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
