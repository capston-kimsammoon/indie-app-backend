# app/models/user_performance_open_alarm.py
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from app.database import Base

class UserPerformanceOpenAlarm(Base):
    __tablename__ = "user_performance_open_alarm"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True, index=True)
    performance_id = Column(Integer, ForeignKey("performance.id"), primary_key=True, index=True)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "performance_id"),
    )
