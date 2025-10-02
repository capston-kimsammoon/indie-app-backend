# app/crud/performance.py
from sqlalchemy.orm import Session
from sqlalchemy import case, and_, or_
from sqlalchemy.sql.expression import func
from datetime import date, datetime
from typing import List, Optional
from app.models.performance import Performance
from app.models.venue import Venue
from app.models.artist import Artist

from app.models.performance_artist import PerformanceArtist
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.models.user_favorite_artist import UserFavoriteArtist   


def get_performances_only_supposed( # 이미 끝난 공연 안 나오게끔 (날짜, 시간 둘다 고려)
    db: Session,
    region: Optional[List[str]],
    sort: str,
    page: int,
    size: int,
) -> (List[Performance], int):
    query = db.query(Performance).join(Venue)

    # ✅ 지역 필터
    if region:
        region = [r.strip() for r in region if r and r.strip() != "전체"]
        if region:
            query = query.filter(Venue.region.in_(region))

    # ✅ 오늘 이후 or 오늘인데 아직 시작 전인 공연만 필터링
    today = date.today()
    now_t = datetime.now().time()
    query = query.filter(
        or_(
            Performance.date > today,
            and_(
                Performance.date == today,
                or_(
                    Performance.time == None,   # 시간이 없으면 포함
                    Performance.time >= now_t  # 시간이 현재 이후
                )
            )
        )
    )

    # 정렬 조건
    if sort == "date":
        query = query.order_by(Performance.date.asc(), Performance.time.asc())
    elif sort == "created_at":
        query = query.order_by(Performance.created_at.desc())
    elif sort == "likes":
        query = (
            query.outerjoin(UserFavoritePerformance, UserFavoritePerformance.performance_id == Performance.id)
            .group_by(Performance.id, Venue.id)
            .order_by(func.count(UserFavoritePerformance.user_id).desc())
        )

    total = query.count()
    performances = query.offset((page - 1) * size).limit(size).all()
    return performances, total


def get_today_performances(db: Session) -> List[Performance]:
    today = date.today()
    return (
        db.query(Performance)
        .join(Venue)
        .filter(Performance.date == today)
        .all()
    )

def get_recent_performances(db: Session, limit: int) -> List[Performance]:

    today = date.today()
    now_t = datetime.now().time()

    return (
        db.query(Performance)
        .join(Venue)
        # 오늘 이후 or 오늘인데 시작 전인 공연만 남김
        .filter(
            or_(
                Performance.date > today,
                and_(
                    Performance.date == today,
                    or_(
                        Performance.time == None,     
                        Performance.time >= now_t     
                    )
                )
            )
        )
        .order_by(Performance.created_at.desc())
        .limit(limit)
        .all()
    )

def get_ticket_opening_performances(db: Session, start: date, end: date) -> List[Performance]:
   
    q = (
        db.query(Performance)
        .join(Venue)
        .filter(Performance.ticket_open_date >= start)
        .filter(Performance.ticket_open_date <= end)
    )

   
    today = date.today()
    if start <= today <= end:
        now_t = datetime.now().time()
        q = q.filter(
            or_(
                Performance.ticket_open_date > today,
                and_(
                    Performance.ticket_open_date == today,
                    or_(
                        Performance.ticket_open_time == None,
                        Performance.ticket_open_time >= now_t
                    )
                )
            )
        )

    # 임박순 정렬 + 최대 6개
    return (
        q.order_by(
            Performance.ticket_open_date.asc(),
            case((Performance.ticket_open_time == None, 1), else_=0).asc(),
            Performance.ticket_open_time.asc(),
        )
        .limit(6)
        .all()
    )

def get_recommendation_performances(db: Session, user_id: int) -> List[Performance]:
   
    # 추천 6개 (부족하면 있는 만큼):
    # A 3개: 나와 같은 가수를 찜한 사용자들이 찜한 다른 공연
    # B 3개: 내가 찜한 공연을 찜한 사용자들이 찜한 다른 공연
    # 각 묶음 랜덤, 합칠 때 중복 제거, 최대 6개
    
    # 내가 찜한 공연 (중복 제거/제외용)
    liked_perf_ids_subq = (
        db.query(UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id == user_id)
        .subquery()
    )

    # 내가 찜한 아티스트
    liked_artist_ids_subq = (
        db.query(UserFavoriteArtist.artist_id)
        .filter(UserFavoriteArtist.user_id == user_id)
        .subquery()
    )
    # 같은 아티스트를 찜한 '다른' 사용자
    users_like_same_artists_subq = (
        db.query(UserFavoriteArtist.user_id)
        .filter(UserFavoriteArtist.artist_id.in_(liked_artist_ids_subq))
        .filter(UserFavoriteArtist.user_id != user_id)
        .distinct()
        .subquery()
    )
    # 그 사용자들이 찜한 공연들(내가 이미 찜한 공연 제외)
    perfs_A = (
        db.query(Performance)
        .join(UserFavoritePerformance, Performance.id == UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id.in_(users_like_same_artists_subq))
        .filter(~Performance.id.in_(liked_perf_ids_subq))
        .order_by(func.rand())
        .limit(3)
        .all()
    )

    # 내가 찜한 공연을 찜한 '다른' 사용자
    users_like_my_perfs_subq = (
        db.query(UserFavoritePerformance.user_id)
        .filter(UserFavoritePerformance.performance_id.in_(liked_perf_ids_subq))
        .filter(UserFavoritePerformance.user_id != user_id)
        .distinct()
        .subquery()
    )
    # 그 사용자들이 찜한 다른 공연(내가 이미 찜한 공연 제외)
    perfs_B = (
        db.query(Performance)
        .join(UserFavoritePerformance, Performance.id == UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id.in_(users_like_my_perfs_subq))
        .filter(~Performance.id.in_(liked_perf_ids_subq))
        .order_by(func.rand())
        .limit(3)
        .all()
    )

    # ===== 합치고 중복 제거, 최대 6개 =====
    seen = set()
    merged: List[Performance] = []
    for p in perfs_A + perfs_B:
        if p.id in seen:
            continue
        seen.add(p.id)
        merged.append(p)
        if len(merged) >= 6:
            break

    return merged

def get_performances(
    db: Session,
    region: Optional[List[str]],
    sort: str,
    page: int,
    size: int,
) -> (List[Performance], int):
    query = db.query(Performance).join(Venue)

    if region:
        region = [r.strip() for r in region if r and r.strip() != "전체"]
        if region:
            query = query.filter(Venue.region.in_(region))

    if sort == "date":
        query = query.order_by(Performance.date.asc())
    elif sort == "created_at":
        query = query.order_by(Performance.created_at.desc())
    elif sort == "likes":
        query = (
            query.outerjoin(UserFavoritePerformance, UserFavoritePerformance.performance_id == Performance.id)
            .group_by(Performance.id, Venue.id)
            .order_by(func.count(UserFavoritePerformance.user_id).desc())
        )

    total = query.count()
    performances = query.offset((page - 1) * size).limit(size).all()
    return performances, total

def get_performance_detail(db: Session, performance_id: int) -> Optional[Performance]:
    return db.query(Performance).filter(Performance.id == performance_id).first()

def get_performance_artists(db: Session, performance_id: int) -> List[Artist]:
    return (
        db.query(Artist)
        .join(PerformanceArtist, PerformanceArtist.artist_id == Artist.id)
        .filter(PerformanceArtist.performance_id == performance_id)
        .all()
    )

def is_user_liked_performance(db: Session, user_id: int, performance_id: int) -> bool:
    return db.query(UserFavoritePerformance).filter_by(user_id=user_id, performance_id=performance_id).first() is not None

def is_user_alarmed_performance(db: Session, user_id: int, performance_id: int) -> bool:
    return db.query(UserPerformanceTicketAlarm).filter_by(user_id=user_id, performance_id=performance_id).first() is not None

def get_performance_like_count(db: Session, performance_id: int) -> int:
    return db.query(UserFavoritePerformance).filter_by(performance_id=performance_id).count()
