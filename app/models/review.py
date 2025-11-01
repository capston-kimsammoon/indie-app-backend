# app/models/review.py
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Review(Base):
    __tablename__ = "review"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    user = relationship("User", back_populates="reviews")
    venue = relationship("Venue", back_populates="reviews")
    images = relationship("ReviewImage", back_populates="review", cascade="all, delete-orphan")
    likes  = relationship("ReviewLike",  back_populates="review", cascade="all, delete-orphan")
    reports = relationship("ReviewReport", back_populates="review", cascade="all, delete-orphan")
