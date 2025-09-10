from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class ReviewLike(Base):
    __tablename__ = "review_like"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    review_id = Column(Integer, ForeignKey("review.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "review_id", name="unique_user_review_like"),
    )

    review = relationship("Review", back_populates="likes")
