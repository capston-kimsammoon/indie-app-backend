# app/crud/comment.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate
from datetime import datetime

def create_reply(
    db: Session,
    post_id: int,
    parent_comment_id: int,
    user_id: int,
    comment_data: CommentCreate
):
    parent_comment = db.query(Comment).filter(Comment.id == parent_comment_id).first()
    if parent_comment is None:
        raise HTTPException(status_code=400, detail="부모 댓글이 존재하지 않습니다.")

    comment = Comment(
        content=comment_data.content,
        post_id=post_id,
        parent_comment_id=parent_comment_id,
        user_id=user_id,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

# 댓글 목록 조회
def get_comments_for_post(db: Session, post_id: int, user_id: int | None, page: int, size: int):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        return None

    query = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    total = query.count()
    offset = (page - 1) * size
    comments = query.offset(offset).limit(size).all()
    total_pages = (total + size - 1) // size

    result = []
    for c in comments:
        result.append({
            "id": c.id,
            "content": c.content,
            "user": {
                "id": c.user.id,
                "nickname": c.user.nickname,
                "profile_url": c.user.profile_url,
            },
            "created_at": c.created_at.isoformat(),
            "isMine": user_id is not None and c.user_id == user_id
        })

    return {
        "page": page,
        "totalPages": total_pages,
        "comment": result,
    }

# 댓글 작성
def create_comment(db: Session, post_id: int, user_id: int, content: str):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        return None

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        created_at=datetime.utcnow()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

# 댓글 수정
def update_comment(db: Session, post_id: int, comment_id: int, user_id: int, content: str):
    comment = db.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
    if not comment or comment.user_id != user_id:
        return None

    comment.content = content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)
    return comment

# 댓글 삭제
def delete_comment(db: Session, post_id: int, comment_id: int, user_id: int):
    comment = db.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
    if not comment or comment.user_id != user_id:
        return None

    db.delete(comment)
    db.commit()
    return comment_id