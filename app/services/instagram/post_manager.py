# app/services/instagram/post_manager.py
# 중복 검사하고 데이터베이스에 저장

from sqlalchemy.orm import Session
from app import models, schemas

# 같은 게시물 중복 저장 방지
def is_duplicate_post(db: Session, shortcode: str) -> bool:
    return db.query(models.Performance).filter(models.Performance.shortcode == shortcode).first() is not None

# 게시물 정보 저장
# extract_performance_info 처리 후에 저장해야 함
def save_post_to_db(db: Session, post_data: dict):
    new_post = models.Performance(
        instagram_url=post_data["url"],
        content=post_data["text"],
        image_url=post_data["image_url"],
        artist_name=post_data.get("artist_name"),
        performance_date=post_data.get("date"),
        venue_name=post_data.get("venue"),
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post