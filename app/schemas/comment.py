# app/schemas/comment.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# 댓글 작성 요청 시 사용하는 모델
class CommentCreate(BaseModel):
    content: str

# 댓글 작성자 정보를 담는 서브 모델 (댓글 응답용)
class CommentUser(BaseModel):
    id: int
    nickname: str
    profile_url: Optional[str]

    class Config:
        from_attributes = True

# 댓글 응답 시 사용하는 전체 모델
class CommentResponse(BaseModel):
    id: int
    content: str
    user: CommentUser
    created_at: datetime
    parent_comment_id: Optional[int]
    isMine: bool

    class Config:
        from_attributes = True
