# models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String(100), unique=True, index=True, nullable=False) # 회원가입은 한 계정당 한 번만 가능
    nickname = Column(String(100), unique=True) # 닉네임 중복 방지 
    profile_url = Column(String(300), nullable=True)
    alarm_enabled = Column(Boolean, nullable=False)
    location_enabled = Column(Boolean, nullable=False)

    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    favorite_artists = relationship("Artist", secondary="user_favorite_artist", back_populates="favorite_users")
    favorite_performances = relationship("Performance", secondary="user_favorite_performance", back_populates="favorite_users")
    ticket_alarm_performances = relationship("Performance", secondary="user_performance_ticketalarm", back_populates="ticket_alarm_users")