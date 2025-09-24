# app/models/review_like.py
from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base

class ReviewLike(Base):
    __tablename__ = "review_like"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)  # ✅ 추천

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    review = relationship("Review", back_populates="likes")
    user = relationship("User", back_populates="review_likes")

    __table_args__ = (
        UniqueConstraint("review_id", "user_id", name="uq_review_like_review_user"),  # 같은 유저가 같은 리뷰에 1회만
    ) # 같은 사용자가 리뷰에 좋아요를 중복으로 누르지 않게 하기 위해 
