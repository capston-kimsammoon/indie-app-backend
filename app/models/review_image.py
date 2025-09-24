# app/models/review_image.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class ReviewImage(Base):
    __tablename__ = "review_image"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(300), nullable=False)  # ERD 표기 그대로

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    review = relationship("Review", back_populates="images")
