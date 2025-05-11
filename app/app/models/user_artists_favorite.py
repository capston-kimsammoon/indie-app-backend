from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UserArtistFavorite(Base):
    __tablename__ = "user_artists_favorite"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)