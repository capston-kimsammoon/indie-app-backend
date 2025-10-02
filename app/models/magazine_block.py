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

    order = Column(Integer, nullable=False, default=0)

    type = Column(Enum(*MagBlockType, name="mag_block_type"), nullable=False, server_default="text")

    text = Column(Text)

    image_url = Column(String(500))
    caption = Column(String(300))
    align = Column(Enum(*ImgAlignType, name="mag_img_align"), server_default="center")

    meta = Column(JSON)

    magazine = relationship("Magazine", back_populates="blocks")
