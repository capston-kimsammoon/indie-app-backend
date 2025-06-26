from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UserPerformanceFavorite(Base):
    __tablename__ = "user_performances_favorite"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), primary_key=True)
    
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "performance_id"),
    )