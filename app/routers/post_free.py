from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import Optional
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.post import Post
from app.models.user import User
from app.models.post_like import PostLike
from app.utils.dependency import get_current_user, get_current_user_optional
from sqlalchemy import func

router = APIRouter(prefix="/post", tags=["Post"])

# 자유게시판 1. 글 목록 조회
@router.get("")
def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    sort: str = Query("recent"),  # "recent", "like", etc.
    type: str = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional),  # 인증 없이도 가능
):
    query = db.query(Post)

    if type:
        query = query.filter(Post.type == type)

    total = query.count()

    if sort == "like":
        query = query.outerjoin(PostLike).group_by(Post.id).order_by(func.count(PostLike.id).desc())
    else:
        query = query.order_by(Post.created_at.desc())

    posts = query.offset((page - 1) * size).limit(size).all()

    response = {
        "page": page,
        "totalPages": (total + size - 1) // size,
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "author": post.user.nickname,
                "likeCount": len(post.like),
                "commentCount": len(post.comments),  # assuming .comments relationship exists
                "thumbnail": post.thumbnail_url,
            }
            for post in posts
        ]
    }
    return response


# 자유게시판 2. 게시물 상세 정보 조회
@router.get("/{post_id}")
def get_post_detail(
    post_id: int = Path(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user_optional),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    is_liked = False
    is_mine = False

    if user:
        is_liked = db.query(PostLike).filter_by(user_id=user.id, post_id=post.id).first() is not None
        is_mine = user.id == post.user_id

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user": {
            "id": post.user.id,
            "nickname": post.user.nickname,
        },
        "created_at": post.created_at.isoformat(),
        "likeCount": len(post.like),
        "commentCount": len(post.comments),
        "isLiked": is_liked,
        "isMine": is_mine,
        "images": [image.url for image in post.images],  # assuming relationship exists
    }


# 자유게시판 3-1. 좋아요 ON
@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if db.query(PostLike).filter_by(user_id=user.id, post_id=post_id).first():
        raise HTTPException(status_code=409, detail="Already liked")

    like = PostLike(user_id=user.id, post_id=post_id)
    db.add(like)
    db.commit()
    return {"message": "Post liked"}


# 자유게시판 3-2. 좋아요 OFF
@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    like = db.query(PostLike).filter_by(user_id=user.id, post_id=post_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return


# Optional 인증 유저 dependency
from fastapi import Security

def get_current_user_optional(
    user: Optional[User] = Depends(get_current_user_optional)
) -> User:
    return user
