# app/crud/alert.py
from sqlalchemy.orm import Session

from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.models.user_performance_open_alarm import UserPerformanceOpenAlarm


def create_alert(db: Session, user_id: int, type: str, ref_id: int):
    if type == "performance":
        exists = (
            db.query(UserPerformanceTicketAlarm)
            .filter_by(user_id=user_id, performance_id=ref_id)
            .first()
        )
        if exists:
            return None
        db.add(UserPerformanceTicketAlarm(user_id=user_id, performance_id=ref_id))

    elif type == "artist":
        exists = (
            db.query(UserArtistTicketAlarm)
            .filter_by(user_id=user_id, artist_id=ref_id)
            .first()
        )
        if exists:
            return None
        db.add(UserArtistTicketAlarm(user_id=user_id, artist_id=ref_id))

    elif type == "ticket_open":
        exists = (
            db.query(UserPerformanceOpenAlarm)
            .filter_by(user_id=user_id, performance_id=ref_id)
            .first()
        )
        if exists:
            return None
        db.add(UserPerformanceOpenAlarm(user_id=user_id, performance_id=ref_id))

    else:
        return False

    db.commit()
    return True


def delete_alert(db: Session, user_id: int, type: str, ref_id: int):
    if type == "performance":
        alert = (
            db.query(UserPerformanceTicketAlarm)
            .filter_by(user_id=user_id, performance_id=ref_id)
            .first()
        )
    elif type == "artist":
        alert = (
            db.query(UserArtistTicketAlarm)
            .filter_by(user_id=user_id, artist_id=ref_id)
            .first()
        )
    elif type == "ticket_open":
        alert = (
            db.query(UserPerformanceOpenAlarm)
            .filter_by(user_id=user_id, performance_id=ref_id)
            .first()
        )
    else:
        return False

    if not alert:
        return None

    db.delete(alert)
    db.commit()
    return True
