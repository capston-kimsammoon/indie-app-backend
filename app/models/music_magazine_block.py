# app/models/music_magazine_block.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base

# 블록 유형: 소제목/본문(text), 이미지(image), 구분선(divider), 버튼/링크(cta)
MusicMagBlockType = ("text", "image", "divider", "cta")

class MusicMagazineBlock(Base):
    __tablename__ = "music_magazine_block"

    id = Column(Integer, primary_key=True)

    magazine_id = Column(
        Integer,
        ForeignKey("music_magazine.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )

    # 예약어 피하려고 order 대신 display_order 사용
    display_order = Column(Integer, nullable=False, default=0)

    type = Column(
        Enum(*MusicMagBlockType, name="music_mag_block_type"),
        nullable=False
    )

    # text 블록용: 소제목/본문 중 필요한 것만 채움(하나만 채워도 됨)
    semititle = Column(String(200))   # 소제목 전용
    text = Column(Text)               # 본문 전용

    # image 블록용
    image_url = Column(String(500))

    # cta 블록용(아티스트 페이지로 이동)
    artist_id = Column(Integer, ForeignKey("artist.id"))

    magazine = relationship("MusicMagazine", back_populates="blocks")
    # Artist 관계는 선택 사항이라 생략(artist_id로 링크 생성)
