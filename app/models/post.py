# app/models/post.py
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
    thumbnail_filename = Column(String, nullable=True)

    # 상대 경로만 반환 (/static/uploads/...)
    @property
    def thumbnail_path(self) -> str:
        name = (self.thumbnail_filename or "").strip()
        if not name:
            return "/static/uploads/default_image.jpg"
        if name.startswith("/"):
            return name
        return f"/static/uploads/{name}"

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    like = relationship("PostLike", back_populates="post")
    images = relationship("PostImage", back_populates="post", cascade="all, delete-orphan")
