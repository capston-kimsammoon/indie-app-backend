from sqlalchemy.orm import Session
from datetime import datetime
from app.models.artist import Artist
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.performance_artist import PerformanceArtist
from app.models.performance import Performance

# 아티스트 목록 조회 (페이징 포함, 찜 여부 포함)
def get_artist_list(db: Session, user_id: int | None, page: int, size: int):
    query = db.query(Artist)
    total = query.count()
    offset = (page - 1) * size
    artists = query.offset(offset).limit(size).all()

    result = []
    for artist in artists:
        is_liked = False
        if user_id:
            is_liked = db.query(UserFavoriteArtist).filter_by(user_id=user_id, artist_id=artist.id).first() is not None
        result.append({
            "id": artist.id,
            "name": artist.name,
            "image_url": artist.image_url,
            "isLiked": is_liked
        })

    return {
        "page": page,
        "totalPages": (total + size - 1) // size,
        "artists": result
    }

# 아티스트 상세 정보 + 예정/지난 공연 목록 + 찜 여부 포함
def get_artist_detail(db: Session, artist_id: int, user_id: int | None):
    artist = db.query(Artist).filter_by(id=artist_id).first()
    if not artist:
        return None

    is_liked = False
    if user_id:
        is_liked = db.query(UserFavoriteArtist).filter_by(user_id=user_id, artist_id=artist_id).first() is not None

    now = datetime.now()
    performance_ids = db.query(PerformanceArtist.performance_id).filter_by(artist_id=artist_id).subquery()
    performances = db.query(Performance).filter(Performance.id.in_(performance_ids)).all()

    upcoming, past = [], []
    for p in performances:
        perf_data = {
            "id": p.id,
            "title": p.title,
            "date": f"{p.date}T{p.time.strftime('%H:%M')}",
            "image_url": p.image_url
        }
        if datetime.combine(p.date, p.time) >= now:
            upcoming.append(perf_data)
        else:
            past.append(perf_data)

    return {
        "id": artist.id,
        "name": artist.name,
        "image_url": artist.image_url,
        "spotify_url": artist.spotify_url,
        "instagram_account": artist.instagram_account,
        "isLiked": is_liked,
        "upcomingPerformances": upcoming,
        "pastPerformances": past
    }
