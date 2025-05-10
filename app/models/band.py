from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Band(Base):
    __tablename__ = "bands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    # genre = Column(String(100))
    # spotify_url = Column(String(200))
    image_url = Column(String(200))
    instagram_account = Column(String(100))

    artists = relationship("Artist", back_populates="band")