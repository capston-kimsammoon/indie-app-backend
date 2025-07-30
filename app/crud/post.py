# app/crud/post.py
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.post import Post
from app.models.post_image import PostImage
import datetime

# 게시물과 이미지 URL들을 생성하여 DB에 저장
def create_post(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    image_urls: Optional[List[str]] = None
):
    post = Post(
        user_id=user_id,
        title=title,
        content=content,
        created_at=datetime.datetime.utcnow()
    )
    db.add(post)
    db.commit()
    db.refresh(post)

    if image_urls:
        for url in image_urls:
            post_image = PostImage(post_id=post.id, image_url=url)
            db.add(post_image)
        db.commit()

    db.refresh(post)
    return post

# post_id로 게시물 단건 조회
def get_post_by_id(db: Session, post_id: int):
    return db.query(Post).filter(Post.id == post_id).first()

# 게시물 DB에서 삭제
def delete_post(db: Session, post: Post):
    db.delete(post)
    db.commit()