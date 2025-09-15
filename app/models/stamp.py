# app/models/stamp.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Stamp(Base):
    __tablename__ = "stamp"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    performance_id = Column(Integer, ForeignKey("performance.id"), primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "performance_id"),
    )

    # ✅ Performance/User 와의 양방향 관계 (back_populates 이름을 다른 모델과 '정확히' 맞춤)
    user = relationship("User", back_populates="stamps")
    performance = relationship("Performance", back_populates="stamps")
