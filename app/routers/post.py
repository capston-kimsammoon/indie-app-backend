from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Path
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from uuid import uuid4

# 의존성
from app.database import get_db
from app.utils.dependency import get_current_user
from app.utils.dependency import get_current_user, get_current_user_optional

# models
from app.models.user import User

# schemas
from app.schemas import post as post_schema
from app.schemas import comment as comment_schema
from app.schemas import user as user_schema
from app.schemas.post import PostListResponse, PostDetailResponse, PostListItem

# crud
from app.crud import post as crud_post
from app.crud import comment as comment_crud
from app.crud import post as post_crud

router = APIRouter(
    prefix="/post",
    tags=["Post"]
)

# 게시물 작성 (이미지 여러 장 첨부 가능)
@router.post("", response_model=post_schema.PostRead)
async def create_post(
    title: str = Form(...),
    content: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_urls = []
    if images:
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for image in images:
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            save_path = os.path.join(upload_dir, filename)
            with open(save_path, "wb") as f:
                f.write(await image.read())
            image_urls.append(f"/{save_path.replace(os.sep, '/')}")

    post = crud_post.create_post(
        db=db,
        user_id=current_user.id,
        title=title,
        content=content,
        image_urls=image_urls
    )

    return post_schema.PostRead(
        id=post.id,
        title=post.title,
        content=post.content,
        user=user_schema.UserRead.from_orm(post.user),
        imageURLs=[img.image_url for img in post.images],
        created_at=post.created_at
    )

# 게시물 삭제
@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post = crud_post.get_post_by_id(db, post_id)

    if not post:
        raise HTTPException(status_code=404, detail="게시물이 존재하지 않습니다.")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 게시물만 삭제할 수 있습니다.")

    crud_post.delete_post(db, post)

# 1. 자유게시판 글 목록 조회
@router.get("", response_model=PostListResponse)
def get_posts(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    sort: str = Query("recent"),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    total, posts = post_crud.get_post_list(db, page, size, sort, type)
    return {
        "page": page,
        "totalPages": (total + size - 1) // size,
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "author": post.user.nickname,
                "likeCount": len(post.like),
                "commentCount": len(post.comments),
                "thumbnail": post.thumbnail_url,
            }
            for post in posts
        ]
    }

# 2. 게시물 상세 조회
@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post_detail(
    post_id: int = Path(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    post = post_crud.get_post_detail(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    is_liked = user and post_crud.is_post_liked(db, user.id, post.id)
    is_mine = user and user.id == post.user_id

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user": {"id": post.user.id, "nickname": post.user.nickname},
        "created_at": post.created_at.isoformat(),
        "likeCount": len(post.like),
        "commentCount": len(post.comments),
        "isLiked": is_liked,
        "isMine": is_mine,
        "images": [img.url for img in post.images],
    }

# 3-1. 좋아요 ON
@router.post("/{post_id}/like", status_code=status.HTTP_201_CREATED)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    post = post_crud.get_post_detail(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_crud.is_post_liked(db, user.id, post_id):
        raise HTTPException(status_code=409, detail="Already liked")

    post_crud.create_post_like(db, user.id, post_id)
    return {"message": "Post liked"}

# 3-2. 좋아요 OFF
@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not post_crud.is_post_liked(db, user.id, post_id):
        raise HTTPException(status_code=404, detail="Like not found")

    post_crud.delete_post_like(db, user.id, post_id)
