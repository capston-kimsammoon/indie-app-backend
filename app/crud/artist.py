from sqlalchemy.orm import Session
from datetime import datetime
from app.models.artist import Artist
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.performance_artist import PerformanceArtist
from app.models.performance import Performance
from app.utils.text_utils import clean_title   # ✅ 유틸에서 가져옴
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm  # ✅ 추가!

# 아티스트 목록 조회 (변경 없음)
def get_artist_list(db: Session, user_id: int | None, page: int, size: int):
    query = db.query(Artist)
    total = query.count()
    offset = (page - 1) * size
    artists = query.offset(offset).limit(size).all()

    result = []
    for artist in artists:
        is_liked = db.query(UserFavoriteArtist).filter_by(user_id=user_id, artist_id=artist.id).first() is not None if user_id else False
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

# 아티스트 상세 조회 (✅ 공연 제목 clean_title 적용)

def get_artist_detail(db: Session, artist_id: int, user_id: int | None):
    artist = db.query(Artist).filter_by(id=artist_id).first()
    if not artist:
        return None

    # ✅ 찜 여부
    is_liked = (
        db.query(UserFavoriteArtist)
        .filter_by(user_id=user_id, artist_id=artist_id)
        .first()
        is not None if user_id else False
    )

    # ✅ 알림 여부 (추가)
    is_notified = (
        db.query(UserArtistTicketAlarm)
        .filter_by(user_id=user_id, artist_id=artist_id)
        .first()
        is not None if user_id else False
    )

    # ✅ 관련 공연 가져오기
    performance_ids = db.query(PerformanceArtist.performance_id).filter_by(artist_id=artist_id).subquery()
    performances = db.query(Performance).filter(Performance.id.in_(performance_ids)).all()

    upcoming, past = [], []
    now = datetime.now()
    for p in performances:
        perf_data = {
            "id": p.id,
            "title": clean_title(p.title),
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
        "isNotified": is_notified,  # ✅ 여기 포함!
        "upcomingPerformances": upcoming,
        "pastPerformances": past
    }