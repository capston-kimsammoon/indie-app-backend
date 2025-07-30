from sqlalchemy.orm import Session
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm

def create_alert(db: Session, user_id: int, type: str, ref_id: int):
    if type == "performance":
        exists = db.query(UserPerformanceTicketAlarm).filter_by(user_id=user_id, performance_id=ref_id).first()
        if exists:
            return None
        alert = UserPerformanceTicketAlarm(user_id=user_id, performance_id=ref_id)
        db.add(alert)

    elif type == "artist":
        exists = db.query(UserArtistTicketAlarm).filter_by(user_id=user_id, artist_id=ref_id).first()
        if exists:
            return None
        alert = UserArtistTicketAlarm(user_id=user_id, artist_id=ref_id)
        db.add(alert)

    else:
        return False

    db.commit()
    return True

def delete_alert(db: Session, user_id: int, type: str, ref_id: int):
    if type == "performance":
        alert = db.query(UserPerformanceTicketAlarm).filter_by(user_id=user_id, performance_id=ref_id).first()
    elif type == "artist":
        alert = db.query(UserArtistTicketAlarm).filter_by(user_id=user_id, artist_id=ref_id).first()
    else:
        return False

    if not alert:
        return None

    db.delete(alert)
    db.commit()
    return True
