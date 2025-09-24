# app/models/magazine_block.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from app.database import Base

MagBlockType = ("text", "image", "quote", "embed", "divider")
ImgAlignType = ("left", "center", "right")

class MagazineBlock(Base):
    __tablename__ = "magazine_block"

    id = Column(Integer, primary_key=True)
    magazine_id = Column(Integer, ForeignKey("magazine.id", ondelete="CASCADE"), index=True, nullable=False)

    # ✅ 순서(중간삽입 편하려면 0,10,20...로 운영)
    order = Column(Integer, nullable=False, default=0)

    # ✅ 블록 타입
    type = Column(Enum(*MagBlockType, name="mag_block_type"), nullable=False, server_default="text")

    # TEXT 블록용
    text = Column(Text)

    # IMAGE 블록용
    image_url = Column(String(500))
    caption = Column(String(300))
    align = Column(Enum(*ImgAlignType, name="mag_img_align"), server_default="center")

    # 기타 확장(임베드, 옵션 등)
    meta = Column(JSON)

    magazine = relationship("Magazine", back_populates="blocks")
