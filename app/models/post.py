# app/model/post.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Post(Base):
    __tablename__ = "post"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    title = Column(String(200))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    thumbnail_filename = Column(String(255), nullable=True)

    @property
    def thumbnail_url(self):
        if self.thumbnail_filename:
            return f"https://your.cdn.com/thumbnails/{self.thumbnail_filename}"
        return None

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")
    like = relationship("PostLike", back_populates="post")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")

