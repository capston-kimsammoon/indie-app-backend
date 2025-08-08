# app/routers/comment.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.post import Post
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate 
from app.utils.dependency import get_current_user, get_current_user_optional
from app.crud import comment as comment_crud
from app.schemas import comment as comment_schema

router = APIRouter(tags=["Comment"])


# 댓글 1. 댓글 목록 조회 
@router.get("/post/{post_id}/comment")
def get_comments(
    post_id: int,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    query = db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc())

    total = query.count()
    total_pages = (total + size - 1) // size
    offset = (page - 1) * size

    comments = query.offset(offset).limit(size).all()

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
            "isMine": current_user is not None and c.user_id == current_user.id
        })

    return {
        "page": page,
        "totalPages": total_pages,
        "comment": result,
    }


# 댓글 2. 작성 (인증 필수)
@router.post("/post/{post_id}/comment", status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        post_id=post_id,
        user_id=current_user.id,
        content=comment_data.content,
        created_at=datetime.utcnow()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "content": comment.content,
        "user": {
            "id": current_user.id,
            "nickname": current_user.nickname,
            "profile_url": current_user.profile_url,
        },
        "created_at": comment.created_at.isoformat(),
        "isMine": True,
    }


# 댓글 3. 글 수정 (인증 필수)
@router.patch("/post/{post_id}/comment/{comment_id}")
def update_comment(
    post_id: int,
    comment_id: int,
    comment_data: CommentUpdate,
    db: Session = Depends(get_db),
    
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")

    comment.content = comment_data.content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)

    return {
        "id": comment.id,
        "content": comment.content,
        "user": {
            "id": current_user.id,
            "nickname": current_user.nickname,
            "profile_url": current_user.profile_url,
        },
        "createdAt": comment.created_at.isoformat(),
        "updatedAt": comment.updated_at.isoformat() if comment.updated_at else None,
        "isMine": True,
    }


# 댓글 4. 글 삭제 (인증 필수)
@router.delete("/post/{post_id}/comment/{comment_id}")
def delete_comment(
    post_id: int,
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.post_id == post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    db.delete(comment)
    db.commit()

    return {
        "message": "댓글이 삭제되었습니다.",
        "deletedCommentId": comment_id
    }

# 답글 작성
@router.post("/{post_id}/comment/{comment_id}", response_model=comment_schema.CommentResponse)
def create_comment_reply(
    post_id: int,
    comment_id: int,
    comment_data: comment_schema.CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    comment = comment_crud.create_reply(db, post_id, comment_id, current_user.id, comment_data)

    return comment_schema.CommentResponse(
        id=comment.id,
        content=comment.content,
        user=comment_schema.CommentUser(
            id=current_user.id,
            nickname=current_user.nickname,
            profile_url=current_user.profile_url,
        ),
        created_at=comment.created_at,
        parent_comment_id=comment.parent_comment_id,
        isMine=True
    )

