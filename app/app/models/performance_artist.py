from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PerformanceArtist(Base):
    __tablename__ = "performance_artists"
    performance_id = Column(Integer, ForeignKey("performances.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artists.id"), primary_key=True)