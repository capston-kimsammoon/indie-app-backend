from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Artist(Base):
    __tablename__ = "artist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    image_url = Column(String(200))
    spotify_url = Column(String(200))
    instagram_account = Column(String(100))

    # band = relationship("Band", back_populates="artists")
    performances = relationship("Performance", secondary="performance_artist", back_populates="artists")
    favorite_users = relationship("User", secondary="user_favorite_artist", back_populates="favorite_artists")