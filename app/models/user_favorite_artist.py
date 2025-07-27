from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UserFavoriteArtist(Base):
    __tablename__ = "user_favorite_artist"
    
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artist.id"), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "artist_id"),
    )