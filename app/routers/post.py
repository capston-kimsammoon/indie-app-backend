# app/routers/post.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Path, Request
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
from uuid import uuid4
from datetime import datetime, timezone, timedelta

# 의존성
from app.database import get_db
from app.utils.dependency import get_current_user, get_current_user_optional

# models
from app.models.user import User

# schemas
from app.schemas import post as post_schema
from app.schemas import user as user_schema
from app.schemas.post import PostListResponse, PostDetailResponse

# crud
from app.crud import post as crud_post
from app.crud import post as post_crud

router = APIRouter(
    prefix="/post",
    tags=["Post"]
)

# BASE_DIR / STATIC_DIR 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# ----- 시간 변환 유틸: UTC/naive -> KST ISO -----
KST = timezone(timedelta(hours=9))

def to_kst_iso(dt: Optional[datetime]) -> Optional[str]:
    """naive는 UTC로 간주해서 tzinfo 채운 뒤 KST로 변환해 isoformat 반환"""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST).isoformat()

def to_abs(base: str, u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    u = u.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/"):
        return f"{base.rstrip('/')}{u}"
    return f"{base.rstrip('/')}/static/uploads/{u}"

# 1. 게시물 작성 (이미지 여러 장 첨부 가능, 썸네일 포함)
@router.post("", response_model=post_schema.PostRead)
async def create_post(
    request: Request,
    title: str = Form(...),
    content: str = Form(...),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image_urls: List[str] = []
    thumbnail_filename: Optional[str] = None

    if images:
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for idx, image in enumerate(images):
            ext = os.path.splitext(image.filename)[1]
            filename = f"{uuid4().hex}{ext}"
            save_path = os.path.join(upload_dir, filename)

            with open(save_path, "wb") as f:
                f.write(await image.read())

            rel_url = f"/static/uploads/{filename}"
            image_urls.append(rel_url)

            if idx == 0:
                thumbnail_filename = filename

    post = crud_post.create_post(
        db=db,
        user_id=current_user.id,
        title=title,
        content=content,
        image_urls=image_urls,
        thumbnail_filename=thumbnail_filename
    )

    base = str(request.base_url)

    return post_schema.PostRead(
        id=post.id,
        title=post.title,
        content=post.content,
        user=user_schema.UserRead.from_orm(post.user),
        imageURLs=[to_abs(base, img.image_url) for img in post.images],
        thumbnail_filename=post.thumbnail_filename,
        thumbnail_url=to_abs(base, getattr(post, "thumbnail_path", None) or post.thumbnail_filename),
        created_at=to_kst_iso(post.created_at) 
    )

# 2. 게시물 삭제
@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from urllib.parse import urlparse

    post = crud_post.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시물이 존재하지 않습니다.")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 게시물만 삭제할 수 있습니다.")

    # 1) 이미지 파일 삭제
    if post.images:
        for img in post.images:
            image_url = getattr(img, "image_url", None) or getattr(img, "url", None)
            if not image_url:
                continue
            try:
                path = urlparse(image_url).path
                if path.startswith("/static/"):
                    relative_path = path[len("/static/"):]
                else:
                    relative_path = path

                image_path = os.path.join(STATIC_DIR, relative_path)
                if os.path.exists(image_path):
                    os.remove(image_path)
                    print(f"✅ 삭제됨: {image_path}")
                else:
                    print(f"❌ 파일 없음: {image_path}")
            except Exception as e:
                print(f"🔥 이미지 삭제 실패: {e}")

    # 2) 댓글 삭제 (부모-자식 정리)
    from app.models.comment import Comment
    try:
      rows = db.query(Comment.id, Comment.parent_comment_id)\
               .filter(Comment.post_id == post_id).all()

      if rows:
          id_to_parent = {cid: pid for cid, pid in rows}
          child_count = {cid: 0 for cid, _ in rows}
          for cid, pid in rows:
              if pid is not None:
                  child_count[pid] = child_count.get(pid, 0) + 1

          # 말단부터 삭제
          leaves = [cid for cid, pid in rows
                    if pid is not None and child_count.get(cid, 0) == 0]

          while leaves:
              db.query(Comment).filter(Comment.id.in_(leaves))\
                .delete(synchronize_session=False)

              new_leaves = []
              for leaf in leaves:
                  parent = id_to_parent.get(leaf)
                  if parent is None:
                      continue
                  child_count[parent] = max(0, child_count.get(parent, 0) - 1)
                  if child_count[parent] == 0 and id_to_parent.get(parent) is not None:
                      new_leaves.append(parent)
              leaves = new_leaves

          db.query(Comment).filter(Comment.post_id == post_id)\
            .delete(synchronize_session=False)

      # 3) 게시글 삭제
      crud_post.delete_post(db, post)

    except Exception:
      db.rollback()
      raise HTTPException(status_code=500, detail="게시물/댓글 삭제 중 오류가 발생했습니다.")

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

@router.put("/{post_id}")
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    post = crud_post.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="게시물이 존재하지 않습니다.")
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인 게시물만 수정할 수 있습니다.")

    updated = False
    if payload.title is not None:
        post.title = payload.title
        updated = True
    if payload.content is not None:
        post.content = payload.content
        updated = True

    if not updated:
        raise HTTPException(status_code=400, detail="수정할 값이 없습니다.")

    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
    }

# 3. 자유게시판 글 목록 조회
@router.get("", response_model=PostListResponse)
def get_posts(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    sort: str = Query("recent"),
    type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    total, posts = post_crud.get_post_list(db, page, size, sort, type)
    base = str(request.base_url)

    return {
        "page": page,
        "totalPages": (total + size - 1) // size,
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "content": post.content or "",
                "author": post.user.nickname if post.user else "",
                "likeCount": len(post.like) if getattr(post, "like", None) is not None else 0,
                "commentCount": len(post.comments) if getattr(post, "comments", None) is not None else 0,
                "thumbnail": to_abs(base, getattr(post, "thumbnail_path", None) or post.thumbnail_filename),
                "user_id": post.user.id if post.user else None,
            }
            for post in posts
        ]
    }

# 4. 게시물 상세 조회
@router.get("/{post_id}", response_model=PostDetailResponse)
def get_post_detail(
    request: Request,
    post_id: int = Path(...),
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user_optional),
):
    post = post_crud.get_post_detail(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    is_liked = bool(user and post_crud.is_post_liked(db, user.id, post.id))
    is_mine = bool(user and user.id == post.user_id)

    base = str(request.base_url)

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content or "",
        "user": {
            "id": post.user.id if post.user else 0,
            "nickname": post.user.nickname if post.user else "",
            "profile_url": to_abs(base, getattr(post.user, "profile_url", None)) if post.user else None,
        },
        "created_at": to_kst_iso(post.created_at),  # ✅ KST로 변환하여 반환
        "likeCount": len(post.like) if getattr(post, "like", None) is not None else 0,
        "commentCount": len(post.comments) if getattr(post, "comments", None) is not None else 0,
        "isLiked": is_liked,
        "isMine": is_mine,
        "images": [to_abs(base, getattr(img, "image_url", None)) for img in (post.images or [])],
    }

# 5-1. 좋아요 ON
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

# 5-2. 좋아요 OFF
@router.delete("/{post_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not post_crud.is_post_liked(db, user.id, post_id):
        raise HTTPException(status_code=404, detail="Like not found")

    post_crud.delete_post_like(db, user.id, post_id)
