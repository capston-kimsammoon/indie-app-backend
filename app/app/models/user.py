from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String(100), unique=True, index=True)
    nickname = Column(String(100))

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    favorite_artists = relationship("Artist", secondary="user_artists_favorite", back_populates="favorite_users")
    favorite_performances = relationship("Performance", secondary="user_performances_favorite", back_populates="favorite_users")
    ticket_alarm_performances = relationship("Performance", secondary="user_performances_ticketalarm", back_populates="ticket_alarm_users")