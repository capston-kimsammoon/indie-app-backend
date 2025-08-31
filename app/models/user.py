# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    kakao_id = Column(String(100), unique=True, index=True, nullable=False)   # 카카오 고유 ID(문자열로 보관해도 OK)
    nickname = Column(String(100), unique=True)               # 중복 허용 + 인덱스 권장
    profile_url = Column(String(300), nullable=True)

    # ✅ NOT NULL + 기본값(파이썬/DB 모두)
    alarm_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )
    location_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("0"),
    )

    # ✅ 로그아웃/재발급용 리프레시 토큰
    refresh_token = Column(String(512), nullable=True)

    # 관계
    posts = relationship("Post", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    favorite_artists = relationship("Artist", secondary="user_favorite_artist", back_populates="favorite_users")
    favorite_performances = relationship("Performance", secondary="user_favorite_performance", back_populates="favorite_users")
    ticket_alarm_performances = relationship("Performance", secondary="user_performance_ticketalarm", back_populates="ticket_alarm_users")




        