# app/crud/favorite.py (예시)
from sqlalchemy.orm import Session
from sqlalchemy import exists, and_, asc
from app.models.artist import Artist
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm

def get_liked_artists(db: Session, user_id: int, skip: int = 0, limit: int = 10):

    alarm_on = exists().where(and_(
        UserArtistTicketAlarm.user_id == user_id,
        UserArtistTicketAlarm.artist_id == Artist.id
    ))

    q = (db.query(Artist, alarm_on.label("is_alarm_on"))
           .join(UserFavoriteArtist, UserFavoriteArtist.artist_id == Artist.id)
           .filter(UserFavoriteArtist.user_id == user_id)
           .order_by(asc(Artist.name)))

    total = (db.query(UserFavoriteArtist.artist_id)
               .filter(UserFavoriteArtist.user_id == user_id)
               .distinct()
               .count())

    rows = q.offset(skip).limit(limit).all()  # -> (Artist, is_alarm_on_bool)
    return rows, total
