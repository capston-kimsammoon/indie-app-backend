from sqlalchemy.orm import Session
from app.models import UserFavoritePerformance, Performance

# 사용자가 찜한 아티스트 목록과 알림 설정 여부 반환
def get_liked_performances(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    query = (
        db.query(Performance)
        .join(UserFavoritePerformance, Performance.id == UserFavoritePerformance.performance_id)
        .filter(UserFavoritePerformance.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    total = (
        db.query(UserFavoritePerformance)
        .filter(UserFavoritePerformance.user_id == user_id)
        .count()
    )
    return query.all(), total
