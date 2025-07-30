# app/schemas/comment.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    content: str

class CommentUpdate(BaseModel):
    content: str

class CommentUser(BaseModel):
    id: int
    nickname: str
    profile_url: Optional[str]

    class Config:
        orm_mode = True

class CommentResponse(BaseModel):
    id: int
    content: str
    user: CommentUser
    created_at: datetime
    parent_comment_id: Optional[int]
    isMine: bool

    class Config:
        orm_mode = True
