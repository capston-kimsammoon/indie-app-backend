from sqlalchemy.orm import Session
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm

def create_performance_alarms_for_artists(db: Session, performance_id: int, artist_ids: list[int]):
    """
    새로운 공연에 대해 아티스트 알림이 켜져있는 사용자에게 
    UserPerformanceTicketAlarm(공연 알림) 기록을 생성합니다.

    중복 생성 방지를 위해 이미 있으면 생성하지 않습니다.
    """

    # 1. 아티스트 알림 ON인 user_id 리스트 조회
    user_ids = (
        db.query(UserArtistTicketAlarm.user_id)
        .filter(UserArtistTicketAlarm.artist_id.in_(artist_ids))
        .distinct()
        .all()
    )
    user_ids = [uid for (uid,) in user_ids]

    for user_id in user_ids:
        # 2. 공연 알림이 이미 있는지 체크
        exists = (
            db.query(UserPerformanceTicketAlarm)
            .filter_by(user_id=user_id, performance_id=performance_id)
            .first()
        )
        if not exists:
            new_alarm = UserPerformanceTicketAlarm(user_id=user_id, performance_id=performance_id)
            db.add(new_alarm)
    db.commit()
