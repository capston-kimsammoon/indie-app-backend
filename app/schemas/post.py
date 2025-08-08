# app/schemas/post.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 게시물 작성자 정보를 포함한 응답용 유저 모델
class UserRead(BaseModel):
    id: int
    nickname: str
    profile_url: Optional[str]

    class Config:
        from_attributes = True

# 게시물 생성 요청에 사용되는 모델
class PostCreate(BaseModel):
    title: str
    content: str

# 게시물 조회 응답에 사용되는 모델
class PostRead(BaseModel):
    id: int
    title: str
    content: str
    user: UserRead
    imageURLs: List[str]
    thumbnail_filename: Optional[str]
    thumbnail_url: Optional[str]  
    created_at: datetime

    class Config:
        from_attributes = True


class PostUser(BaseModel):
    id: int
    nickname: str
    profile_url: Optional[str] = None  

    class Config:
        from_attributes = True  


class PostListItem(BaseModel):
    id: int
    title: str
    content: str
    author: str
    likeCount: int
    commentCount: int
    thumbnail: Optional[str]

class PostListResponse(BaseModel):
    page: int
    totalPages: int
    posts: List[PostListItem]

class PostDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    user: PostUser
    created_at: str
    likeCount: int
    commentCount: int
    isLiked: bool
    isMine: bool
    images: List[str]