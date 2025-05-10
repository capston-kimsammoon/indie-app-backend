from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    image_url = Column(String(200))
    instagram_account = Column(String(100))
    band_id = Column(Integer, ForeignKey("bands.id"))

    band = relationship("Band", back_populates="artists")
    performances = relationship("Performance", secondary="performance_artists", back_populates="artists")
    favorite_users = relationship("User", secondary="user_artists_favorite", back_populates="favorite_artists")