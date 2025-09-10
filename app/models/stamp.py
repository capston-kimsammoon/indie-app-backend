# models/stamp.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, PrimaryKeyConstraint
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
