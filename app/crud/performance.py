#크루드/퍼포먼스.py
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from datetime import date
from typing import List, Optional
from app.models.performance import Performance
from app.models.venue import Venue
from app.models.artist import Artist

from app.models.performance_artist import PerformanceArtist
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm

def get_today_performances(db: Session) -> List[Performance]:
    today = date.today()
    return (
        db.query(Performance)
        .join(Venue)
        .filter(Performance.date == today)
        .all()
    )

def get_recent_performances(db: Session, limit: int) -> List[Performance]:
    return (
        db.query(Performance)
        .join(Venue)
        .order_by(Performance.created_at.desc())
        .limit(limit)
        .all()
    )

def get_ticket_opening_performances(db: Session, start: date, end: date) -> List[Performance]:
    return (
        db.query(Performance)
        .join(Venue)
        .filter(Performance.ticket_open_date >= start)
        .filter(Performance.ticket_open_date <= end)
        .all()
    )

def get_recommendation_performances(db: Session, user_id: int) -> List[Performance]:
    liked_perf_ids_subq = (
        db.query(UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id == user_id)
        .subquery()
    )

    other_users_subq = (
        db.query(UserFavoritePerformance.user_id)
        .filter(UserFavoritePerformance.performance_id.in_(liked_perf_ids_subq))
        .filter(UserFavoritePerformance.user_id != user_id)
        .distinct()
        .subquery()
    )

    return (
        db.query(Performance)
        .join(UserFavoritePerformance, Performance.id == UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id.in_(other_users_subq))
        .filter(~Performance.id.in_(liked_perf_ids_subq))
        .order_by(func.rand())
        .limit(6)
        .all()
    )

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

# 공연 좋아요 수 조회
def get_performance_like_count(db: Session, performance_id: int) -> int:
    return db.query(UserFavoritePerformance).filter_by(performance_id=performance_id).count()
