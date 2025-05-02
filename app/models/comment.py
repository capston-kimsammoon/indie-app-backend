from sqlalchemy import Column, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")