from sqlalchemy.orm import Session
from sqlalchemy import exists, and_, asc, desc
from app.models.performance import Performance
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm

def get_liked_performances(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 10,
    sort: str = "date"  
):

    is_alarmed = exists().where(and_(
        UserPerformanceTicketAlarm.user_id == user_id,
        UserPerformanceTicketAlarm.performance_id == Performance.id
    ))

    q = (db.query(Performance, is_alarmed.label("is_alarmed"))
           .join(UserFavoritePerformance, UserFavoritePerformance.performance_id == Performance.id)
           .filter(UserFavoritePerformance.user_id == user_id))

    # 정렬
    if sort == "created_at":
        q = q.order_by(desc(Performance.created_at))
    else:  # date 또는 recent 기본: 공연일 가까운 순
        q = q.order_by(asc(Performance.date), asc(Performance.time))

    total = (db.query(UserFavoritePerformance.performance_id)
               .filter(UserFavoritePerformance.user_id == user_id)
               .distinct()
               .count())

    rows = q.offset(skip).limit(limit).all() 
    return rows, total
