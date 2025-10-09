from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from typing import Optional
from app.utils.dependency import get_current_user_optional
from app.models.performance import Performance
from app.models.venue import Venue
from app.models.user import User
from app.models.artist import Artist
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.schemas import search as search_schema
from app.utils.text_utils import clean_title

router = APIRouter(prefix="/search", tags=["Search"])

# 공연 검색
@router.get("/performance", response_model=search_schema.PerformanceSearchResponse)
def search_performance(
    keyword: str = Query(..., description="검색 키워드"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    # 공연 제목에서만 검색
    performance_query = db.query(Performance).join(Venue).filter(
        (Performance.title.ilike(f"%{keyword}%"))
    )
    total = performance_query.count()
    performances = performance_query.offset(skip).limit(size).all()

    performance_items = [
        search_schema.PerformanceSearchItem(
            id=p.id,
            title=clean_title(p.title),
            venue=p.venue.name,
            date=f"{p.date}T{p.time}",
            image_url=p.image_url
        ) for p in performances
    ]

    return search_schema.PerformanceSearchResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        performance=performance_items
    )


# 공연장 검색
@router.get("/venue", response_model=search_schema.VenueSearchResponse)
def search_venue(
    keyword: str = Query(..., description="검색 키워드"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    venue_query = db.query(Venue).filter(Venue.name.ilike(f"%{keyword}%"))
    total = venue_query.count()
    venues = venue_query.offset(skip).limit(size).all()

    venue_items = [
        search_schema.VenueSearchItem(
            id=v.id,
            name=v.name,
            address=v.address,
            image_url=v.image_url
        ) for v in venues
    ]

    return search_schema.VenueSearchResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        venues=venue_items
    )


#  아티스트 검색
@router.get("/artist", response_model=search_schema.ArtistSearchResponse)
def search_artist(
    keyword: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)  # <-- optional로 변경
):
    skip = (page - 1) * size
    artists = db.query(Artist).filter(Artist.name.contains(keyword)).offset(skip).limit(size).all()
    total = db.query(Artist).filter(Artist.name.contains(keyword)).count()

    result = []
    for a in artists:
        isLiked = False
        isAlarmEnabled = False
        if current_user:  # 로그인 유저인 경우만 체크
            isLiked = db.query(UserFavoriteArtist).filter_by(user_id=current_user.id, artist_id=a.id).first() is not None
            isAlarmEnabled = db.query(UserArtistTicketAlarm).filter_by(user_id=current_user.id, artist_id=a.id).first() is not None
        
        result.append(
            search_schema.ArtistSearchItem(
                id=a.id,
                name=a.name,
                profile_url=a.image_url,
                isLiked=isLiked,
                isAlarmEnabled=isAlarmEnabled
            )
        )

    return search_schema.ArtistSearchResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        artists=result
    )

