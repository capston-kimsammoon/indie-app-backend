# models/post_image.py

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PostImage(Base):
    __tablename__ = "post_image"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    image_url = Column(String(300), nullable=False)

    post = relationship("Post", back_populates="images")
