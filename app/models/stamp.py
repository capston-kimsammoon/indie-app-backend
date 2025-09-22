# models/stamp.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
import datetime
from datetime import datetime, timezone

class Stamp(Base):
    __tablename__ = "stamp"

    id = Column(Integer, primary_key=True, index=True)  
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    performance_id = Column(Integer, ForeignKey("performance.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    __table_args__ = (
        UniqueConstraint("user_id", "performance_id", name="unique_user_performance"),
    )

    user = relationship("User", back_populates="stamps")
    performance = relationship("Performance", back_populates="stamps")