from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UserFavoritePerformance(Base):
    __tablename__ = "user_favorite_performance"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    performance_id = Column(Integer, ForeignKey("performance.id"), primary_key=True)
    
    __table_args__ = ( # 복합키 설정
        PrimaryKeyConstraint("user_id", "performance_id"),
    )