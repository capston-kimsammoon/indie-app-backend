from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Artist(Base):
    __tablename__ = "artist"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    image_url = Column(String(300), nullable=True)
    spotify_url = Column(String(300), nullable=True)
    instagram_account = Column(String(100), nullable=True)

    performances = relationship(
        "Performance",
        secondary="performance_artist",
        back_populates="artists",
    )
    favorite_users = relationship(
        "User",
        secondary="user_favorite_artist",
        back_populates="favorite_artists",
    )
