# app/routers/post.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentResponse, CommentUser
from app.crud.comment import create_reply
from app.utils.dependency import get_current_user  # 토큰 인증 시 유저 가져오기

router = APIRouter(
    prefix="/post",
    tags=["Comment"]
)

@router.post("/{post_id}/comment/{comment_id}", response_model=CommentResponse)
def create_comment_reply(
    post_id: int,
    comment_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("get_current_user", get_current_user)
    comment = create_reply(db, post_id, comment_id, current_user.id, comment_data)

    return CommentResponse(
        id=comment.id,
        content=comment.content,
        user=CommentUser(
            id=current_user.id,
            nickname=current_user.nickname,
            profile_url=current_user.profile_url,
        ),
        created_at=comment.created_at,
        parent_comment_id=comment.parent_comment_id,
        isMine=True
    )
