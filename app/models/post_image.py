# models/post_image.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PostImage(Base):
    __tablename__ = "post_image"

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"))
    url = Column(String(255))

    post = relationship("Post", back_populates="images")
