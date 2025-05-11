from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UserArtistFavorite(Base):
    __tablename__ = "user_artists_favorite"
    
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "artist_id"),
    )