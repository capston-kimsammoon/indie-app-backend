from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, backref   # ⬅ backref 추가
from app.database import Base
import datetime

class Comment(Base):
    __tablename__ = "comment"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    post_id = Column(Integer, ForeignKey("post.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comment.id"), nullable=True)

    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

    parent_comment = relationship(
        "Comment",
        remote_side=[id],
        backref=backref(
            "replies",
            cascade="all, delete-orphan",  
            single_parent=True,          
        ),
    )
