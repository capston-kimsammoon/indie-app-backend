# app/crud/comment.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.schemas.comment import CommentCreate

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
