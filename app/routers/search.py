from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.utils.dependency import get_current_user
from app.models.performance import Performance
from app.models.venue import Venue
from app.models.user import User
from app.models.artist import Artist
from app.models.post import Post
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.schemas import search as search_schema
from app.utils.text_utils import clean_title

router = APIRouter(prefix="/search", tags=["Search"])

# 🎯 공연/공연장 검색
@router.get("/performance", response_model=search_schema.PerformanceSearchResponse)
def search_performance_and_venue(
    keyword: str = Query(..., description="검색 키워드"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    performance_query = db.query(Performance).join(Venue).filter(
        (Performance.title.ilike(f"%{keyword}%")) |
        (Venue.name.ilike(f"%{keyword}%"))
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

    venue_items = [
        search_schema.VenueSearchItem(
            id=v.id,
            name=v.name,
            address=v.address,
            image_url=v.image_url
        ) for v in db.query(Venue).filter(Venue.name.ilike(f"%{keyword}%")).all()
    ]

    return search_schema.PerformanceSearchResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        performance=performance_items,
        venue=venue_items
    )

# 🎤 아티스트 검색
@router.get("/artist", response_model=search_schema.ArtistSearchResponse)
def search_artist(
    keyword: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    skip = (page - 1) * size
    artists = db.query(Artist).filter(Artist.name.contains(keyword)).offset(skip).limit(size).all()
    total = db.query(Artist).filter(Artist.name.contains(keyword)).count()

    result = [
        search_schema.ArtistSearchItem(
            id=a.id,
            name=a.name,
            profile_url=a.image_url,
            isLiked=db.query(UserFavoriteArtist).filter_by(user_id=current_user.id, artist_id=a.id).first() is not None,
            isAlarmEnabled=db.query(UserArtistTicketAlarm).filter_by(user_id=current_user.id, artist_id=a.id).first() is not None
        ) for a in artists
    ]

    return search_schema.ArtistSearchResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        artists=result
    )

# 📝 자유게시판 검색
@router.get("/post", response_model=search_schema.PostSearchResponse)
def search_post(
    keyword: str,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db)
):
    skip = (page - 1) * size

    # 🔧 제목 또는 본문에서 키워드 검색 (둘 다 가능하게)
    post_query = db.query(Post).filter(
        or_(
            Post.title.ilike(f"%{keyword}%"),
            Post.content.ilike(f"%{keyword}%")
        )
    )

    total = post_query.count()
    posts = post_query.offset(skip).limit(size).all()

    result = [
        search_schema.PostSearchItem(
            id=p.id,
            title=p.title,
            author=p.user.nickname,
            created_at=p.created_at.date()
        ) for p in posts
    ]

    return search_schema.PostSearchResponse(
        page=page,
        totalPages=(total + size - 1) // size,
        posts=result
    )
