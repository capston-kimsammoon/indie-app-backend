from sqlalchemy.orm import Session
from sqlalchemy import exists, and_, asc, desc
from app.models.performance import Performance
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_performance_open_alarm import UserPerformanceOpenAlarm

def get_liked_performances(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    sort: str = "date"  # "date" | "created_at" | "recent"
):
    """사용자가 찜한 공연 목록 + 각 공연 예매오픈 알림ON 여부 반환 (페이지네이션)"""
    is_alarmed = exists().where(and_(
        UserPerformanceOpenAlarm.user_id == user_id,
        UserPerformanceOpenAlarm.performance_id == Performance.id
    ))

    q = (db.query(Performance, is_alarmed.label("is_alarmed"))
           .join(UserFavoritePerformance, UserFavoritePerformance.performance_id == Performance.id)
           .filter(UserFavoritePerformance.user_id == user_id))

    # 정렬
    if sort == "created_at":
        q = q.order_by(desc(Performance.created_at))
    else:  # "date" 또는 "recent" 기본: 공연일 가까운 순
        q = q.order_by(asc(Performance.date), asc(Performance.time))

    total = (db.query(UserFavoritePerformance.performance_id)
               .filter(UserFavoritePerformance.user_id == user_id)
               .distinct()
               .count())

    rows = q.offset(skip).limit(limit).all()  # -> (Performance, is_alarmed_bool)
    return rows, total
