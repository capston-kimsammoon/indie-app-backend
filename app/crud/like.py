from sqlalchemy.orm import Session
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_favorite_artist import UserFavoriteArtist

def create_like(db: Session, user_id: int, type: str, ref_id: int):
    if type == "performance":
        exists = db.query(UserFavoritePerformance).filter_by(user_id=user_id, performance_id=ref_id).first()
        if exists:
            return None
        like = UserFavoritePerformance(user_id=user_id, performance_id=ref_id)
        db.add(like)

    elif type == "artist":
        exists = db.query(UserFavoriteArtist).filter_by(user_id=user_id, artist_id=ref_id).first()
        if exists:
            return None
        like = UserFavoriteArtist(user_id=user_id, artist_id=ref_id)
        db.add(like)

    else:
        return False

    db.commit()
    return True

def delete_like(db: Session, user_id: int, type: str, ref_id: int):
    if type == "performance":
        like = db.query(UserFavoritePerformance).filter_by(user_id=user_id, performance_id=ref_id).first()
    elif type == "artist":
        like = db.query(UserFavoriteArtist).filter_by(user_id=user_id, artist_id=ref_id).first()
    else:
        return False

    if not like:
        return None

    db.delete(like)
    db.commit()
    return True
