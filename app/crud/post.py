# app/crud/post.py
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.post import Post
from app.models.post_image import PostImage
from app.models.post_like import PostLike
from app.models.user import User
import datetime

# 게시물과 이미지 URL들을 생성하여 DB에 저장
def create_post(
    db: Session,
    user_id: int,
    title: str,
    content: str,
    image_urls: Optional[List[str]] = None,
    thumbnail_filename: Optional[str] = None,
):
    post = Post(
        user_id=user_id,
        title=title,
        content=content,
        created_at=datetime.datetime.utcnow(),
            thumbnail_filename=thumbnail_filename
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


def get_post_list(db: Session, page: int, size: int, sort: str, type: Optional[str]):
    query = db.query(Post)
    if type:
        query = query.filter(Post.type == type)

    total = query.count()

    if sort == "like":
        query = query.outerjoin(PostLike).group_by(Post.id).order_by(func.count(PostLike.id).desc())
    else:
        query = query.order_by(Post.created_at.desc())

    posts = query.offset((page - 1) * size).limit(size).all()
    return total, posts

def get_post_detail(db: Session, post_id: int) -> Optional[Post]:
    return db.query(Post).filter(Post.id == post_id).first()

def is_post_liked(db: Session, user_id: int, post_id: int) -> bool:
    return db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first() is not None

def create_post_like(db: Session, user_id: int, post_id: int):
    like = PostLike(user_id=user_id, post_id=post_id)
    db.add(like)
    db.commit()

def delete_post_like(db: Session, user_id: int, post_id: int):
    like = db.query(PostLike).filter_by(user_id=user_id, post_id=post_id).first()
    if like:
        db.delete(like)
        db.commit()