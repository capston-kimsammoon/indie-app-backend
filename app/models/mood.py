# app/models/mood.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from app.database import Base
import datetime


class Mood(Base):
    __tablename__ = "mood"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, unique=True)  # 무드명 (예: 신나는, 차분한…)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    # 관계 : 이 무드와 연결된 추천 공연 목록
    recommendations = relationship(
        "MoodRecommendation",
        back_populates="mood",
        cascade="all, delete-orphan"
    )


class MoodRecommendation(Base):
    __tablename__ = "mood_recommendation"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    mood_id = Column(Integer, ForeignKey("mood.id", ondelete="CASCADE"), nullable=False)
    performance_id = Column(Integer, ForeignKey("performance.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow)

    # 관계
    mood = relationship("Mood", back_populates="recommendations")
    performance = relationship("Performance", back_populates="mood_recommendations")

    # 제약조건: 한 무드에 같은 공연이 중복 등록되지 않도록
    __table_args__ = (
        UniqueConstraint("mood_id", "performance_id", name="uq_mood_performance"),
        Index("ix_mood_id_created_at", "mood_id", "created_at"),  # 조회·정렬 최적화
    )
