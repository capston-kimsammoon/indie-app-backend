# app/models/review_report.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class ReviewReport(Base):
    __tablename__ = "review_report"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    reason = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    review = relationship("Review", back_populates="reports")
    user = relationship("User")
