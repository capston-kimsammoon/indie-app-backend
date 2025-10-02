# app/crud/artist.py 

from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from datetime import datetime, time as dt_time, timezone, timedelta

from app.models.artist import Artist
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.models.performance_artist import PerformanceArtist
from app.models.performance import Performance
from app.utils.text_utils import clean_title

KST = timezone(timedelta(hours=9))  # 서비스 TZ가 KST이면 사용

# 아티스트 목록 조회 
def get_artist_list(db: Session, user_id: int | None, page: int, size: int):
    q = db.query(Artist)
    total = q.count()
    offset = (page - 1) * size
    artists = q.order_by(asc(Artist.name)).offset(offset).limit(size).all()

    # isLiked 집합 미리 뽑기 
    liked_set = set()
    if user_id:
        artist_ids = [a.id for a in artists]
        if artist_ids:
            rows = (db.query(UserFavoriteArtist.artist_id)
                      .filter(UserFavoriteArtist.user_id == user_id,
                              UserFavoriteArtist.artist_id.in_(artist_ids))
                      .all())
            liked_set = {aid for (aid,) in rows}

    result = [{
        "id": a.id,
        "name": a.name,
        "image_url": a.image_url,
        "isLiked": (a.id in liked_set)
    } for a in artists]

    return {
        "page": page,
        "totalPages": (total + size - 1) // size,
        "artists": result
    }


# 아티스트 상세 조회 
def get_artist_detail(db: Session, artist_id: int, user_id: int | None):
    artist = db.query(Artist).filter_by(id=artist_id).first()
    if not artist:
        return None

    # 찜 여부
    is_liked = False
    if user_id:
        is_liked = db.query(UserFavoriteArtist).filter_by(
            user_id=user_id, artist_id=artist_id
        ).first() is not None

    # 알림 여부
    is_notified = False
    if user_id:
        is_notified = db.query(UserArtistTicketAlarm).filter_by(
            user_id=user_id, artist_id=artist_id
        ).first() is not None

    # 관련 공연 id -> 공연 조회(정렬 포함)
    perf_ids_subq = (db.query(PerformanceArtist.performance_id)
                       .filter(PerformanceArtist.artist_id == artist_id)
                       .subquery())

    perfs = (db.query(Performance)
               .filter(Performance.id.in_(perf_ids_subq))
               .order_by(asc(Performance.date), asc(Performance.time))
               .all())

    now = datetime.now(KST) 
    upcoming, past = [], []

    for p in perfs:
        # 날짜/시간 보정
        if not p.date:
            continue  # 날짜 없으면 스킵
        p_time = p.time or dt_time(0, 0)  # NULL → 00:00
        dt_val = datetime.combine(p.date, p_time, tzinfo=KST)

        # 표시용 문자열
        time_text = p_time.strftime('%H:%M') if p.time else None
        perf_data = {
            "id": p.id,
            "title": clean_title(p.title) if p.title else "",
            "date": f"{p.date.isoformat()}" + (f"T{time_text}" if time_text else ""),
            "image_url": p.image_url
        }

        if dt_val >= now:
            upcoming.append(perf_data)
        else:
            past.append(perf_data)

    # upcoming: 가까운 순, past: 최신이 위로 오게
    def _key(item):
        
        ds = item["date"]
        try:
            return datetime.fromisoformat(ds) if "T" in ds else datetime.fromisoformat(ds + "T00:00")
        except Exception:
            return datetime.max

    upcoming.sort(key=_key)            # 오름차순
    past.sort(key=_key, reverse=True)  # 내림차순

    return {
        "id": artist.id,
        "name": artist.name,
        "image_url": artist.image_url,
        "spotify_url": artist.spotify_url,
        "instagram_account": artist.instagram_account,
        "isLiked": is_liked,
        "isNotified": is_notified,
        "upcomingPerformances": upcoming,
        "pastPerformances": past
    }
