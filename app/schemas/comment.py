# app/schemas/comment.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

# 댓글 작성 요청 시 사용하는 모델
class CommentCreate(BaseModel):
    content: str

class CommentUpdate(BaseModel):
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

# 댓글 생성 요청
class CommentCreate(BaseModel):
    content: str

# 댓글 수정 요청
class CommentUpdate(BaseModel):
    content: str

# 댓글 응답 항목
# class CommentResponse(BaseModel):
#     id: int
#     content: str
#     user: dict 
#     created_at: str
#     isMine: bool

# 댓글 응답 항목 (수정 후)
class CommentUpdateResponse(CommentResponse):
    updatedAt: Optional[str]

# 댓글 목록 응답
class CommentListResponse(BaseModel):
    page: int
    totalPages: int
    comment: List[CommentResponse]

# 댓글 삭제 응답
class CommentDeleteResponse(BaseModel):
    message: str
    deletedCommentId: int