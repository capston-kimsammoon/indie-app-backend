from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from typing import List, Optional
from sqlalchemy.orm import Session
import os
from uuid import uuid4

# 의존성
from app.database import get_db
from app.utils.dependency import get_current_user

# models
from app.models.user import User

# schemas
from app.schemas import post as post_schema
from app.schemas import comment as comment_schema
from app.schemas import user as user_schema

# crud
from app.crud import post as crud_post
from app.crud import comment as comment_crud

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
