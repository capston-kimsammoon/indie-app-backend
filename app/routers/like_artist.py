from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.artist import Artist
from app.models.user_favorite_artist import UserFavoriteArtist
from app.utils.dependency import get_current_user

router = APIRouter(tags=["Artist Likes"])

# 아티스트 3-1. 찜 ON
@router.post("/artist-likes", status_code=status.HTTP_201_CREATED)
def like_artist(
    payload: dict,  # {"type": "artist", "refId": 501}
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if payload.get("type") != "artist":
        raise HTTPException(status_code=400, detail="Unsupported type")

    artist_id = payload.get("refId")
    if not artist_id:
        raise HTTPException(status_code=400, detail="refId is required")

    artist = db.query(Artist).filter(Artist.id == artist_id).first()
    if not artist:
        raise HTTPException(status_code=404, detail="Artist not found")

    existing = db.query(UserFavoriteArtist).filter_by(user_id=user.id, artist_id=artist_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already liked")

    like = UserFavoriteArtist(user_id=user.id, artist_id=artist_id)
    db.add(like)
    db.commit()

    return {"message": "Artist liked"}

# 아티스트 3-2. 찜 OFF
@router.delete("/artist-likes/{artist_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlike_artist(
    artist_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    like = db.query(UserFavoriteArtist).filter_by(user_id=user.id, artist_id=artist_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return
