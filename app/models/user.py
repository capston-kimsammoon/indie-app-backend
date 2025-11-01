# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)

    # --- 소셜/로그인 식별자들 ---
    kakao_id = Column(String(100), unique=True, index=True, nullable=True)  
    login_id = Column(String(12), unique=True, index=True, nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    password_hash = Column(String(255), nullable=True)

    apple_sub = Column(String(255), unique=True, index=True, nullable=True)
    apple_email = Column(String(255), nullable=True)

    # --- 프로필/설정 ---
    nickname = Column(String(100), unique=True, nullable=True)
    profile_url = Column(String(300), nullable=True)
    alarm_enabled = Column(Boolean, nullable=False, server_default=text("0"), default=False)
    location_enabled = Column(Boolean, nullable=False, server_default=text("0"), default=False)

    # 토큰(기존 컬럼)
    refresh_token = Column(String(512), nullable=True)

    # --- 상태/감사 필드 ---
    email_verified = Column(Boolean, nullable=False, server_default=text("0"), default=False)

    # 가입 완료 플래그 (핵심 추가)
    is_completed = Column(Boolean, nullable=False, server_default=text("0"), default=False)

    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # --- 관계 ---
    favorite_artists = relationship("Artist", secondary="user_favorite_artist", back_populates="favorite_users")
    favorite_performances = relationship("Performance", secondary="user_favorite_performance", back_populates="favorite_users")
    ticket_alarm_performances = relationship("Performance", secondary="user_performance_ticketalarm", back_populates="ticket_alarm_users")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    review_likes = relationship("ReviewLike", back_populates="user", cascade="all, delete-orphan")
    stamps = relationship("Stamp", back_populates="user", cascade="all, delete-orphan")
