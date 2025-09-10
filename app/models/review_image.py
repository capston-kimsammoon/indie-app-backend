from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class ReviewImage(Base):
    __tablename__ = "review_image"

    id = Column(Integer, primary_key=True, index=True)
    review_id = Column(Integer, ForeignKey("review.id"), nullable=False)
    image_url = Column(String(300), nullable=False)

    review = relationship("Review", back_populates="images")
