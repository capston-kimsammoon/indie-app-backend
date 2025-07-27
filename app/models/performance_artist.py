from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class PerformanceArtist(Base):
    __tablename__ = "performance_artist"
    performance_id = Column(Integer, ForeignKey("performance.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artist.id"), primary_key=True)

    __table_args__ = ( # 복합키 설정
    PrimaryKeyConstraint("performance_id", "artist_id"),
)
