from sqlalchemy.orm import Session
from app.models import UserFavoriteArtist, Artist

# 사용자가 찜한 공연 목록 페이지네이션하여 반환
def get_liked_artists(db: Session, user_id: int):
    return (
        db.query(Artist)
        .join(UserFavoriteArtist, Artist.id == UserFavoriteArtist.artist_id)
        .filter(UserFavoriteArtist.user_id == user_id)
        .all()
    )
