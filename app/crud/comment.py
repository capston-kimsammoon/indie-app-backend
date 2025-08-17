# app/crud/comment.py
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.post import Post
from app.schemas.comment import CommentCreate


# -----------------------------
# 생성 계열
# -----------------------------
def create_comment(
    db: Session,
    post_id: int,
    user_id: int,
    content: str,
):
    """부모 없는 일반 댓글 생성"""
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="게시글이 존재하지 않습니다.")

    comment = Comment(
        post_id=post_id,
        user_id=user_id,
        content=content,
        created_at=datetime.utcnow(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def create_reply(
    db: Session,
    post_id: int,
    parent_comment_id: int,
    user_id: int,
    comment_data: CommentCreate,
):
    """답글 생성 (parent_comment_id 필수)"""
    parent = db.query(Comment).filter(Comment.id == parent_comment_id).first()
    if parent is None:
        raise HTTPException(status_code=400, detail="부모 댓글이 존재하지 않습니다.")
    if parent.post_id != post_id:
        # 다른 게시글의 댓글에 답글을 붙이려는 경우 방어
        raise HTTPException(status_code=400, detail="부모 댓글의 게시글 ID가 일치하지 않습니다.")

    comment = Comment(
        content=comment_data.content,
        post_id=post_id,
        parent_comment_id=parent_comment_id,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def create_comment_or_reply(
    db: Session,
    post_id: int,
    user_id: int,
    content: str,
    parent_comment_id: int | None = None,
):
    """
    한 엔드포인트에서 댓글/답글 생성 모두 처리하고 싶을 때 사용.
    parent_comment_id가 있으면 답글, 없으면 일반 댓글.
    """
    if parent_comment_id:
        return create_reply(
            db=db,
            post_id=post_id,
            parent_comment_id=parent_comment_id,
            user_id=user_id,
            comment_data=CommentCreate(content=content),
        )
    return create_comment(db=db, post_id=post_id, user_id=user_id, content=content)


# -----------------------------
# 조회
# -----------------------------
def get_comments_for_post(
    db: Session,
    post_id: int,
    user_id: int | None,
    page: int,
    size: int,
):
    post = db.query(Post).filter_by(id=post_id).first()
    if not post:
        return None

    query = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
    )
    total = query.count()
    offset = max(0, (page - 1) * size)
    comments = query.offset(offset).limit(size).all()
    total_pages = (total + size - 1) // size if size > 0 else 1

    result = []
    for c in comments:
        result.append(
            {
                "id": c.id,
                "content": c.content,
                "user": {
                    "id": c.user.id,
                    "nickname": c.user.nickname,
                    "profile_url": c.user.profile_url,
                },
                "created_at": (c.created_at or datetime.utcnow()).isoformat(),
                "parentCommentId": c.parent_comment_id,  # ✅ 프론트 트리 렌더링용
                "isMine": user_id is not None and c.user_id == user_id,
            }
        )

    return {
        "page": page,
        "totalPages": total_pages,
        "comment": result,
    }


# -----------------------------
# 수정/삭제
# -----------------------------
def update_comment(
    db: Session,
    post_id: int,
    comment_id: int,
    user_id: int,
    content: str,
):
    comment = (
        db.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="댓글이 존재하지 않습니다.")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="수정 권한이 없습니다.")

    comment.content = content
    comment.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(
    db: Session,
    post_id: int,
    comment_id: int,
    user_id: int,
):
    # 1) 권한/존재 확인
    comment = db.query(Comment).filter_by(id=comment_id, post_id=post_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="댓글이 존재하지 않습니다.")
    if comment.user_id != user_id:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")

    # 2) 대댓글(자손)부터 모두 수집해서 먼저 삭제
    #    (자기참조 FK 때문에 부모를 먼저 지우면 1451 에러)
    descendants: list[int] = []
    to_visit = [comment_id]

    while to_visit:
        # 현재 레벨의 자식 id 모음
        child_ids = [
            cid for (cid,) in
            db.query(Comment.id)
              .filter(Comment.parent_comment_id.in_(to_visit))
              .all()
        ]
        if not child_ids:
            break
        descendants.extend(child_ids)
        to_visit = child_ids

    if descendants:
        db.query(Comment).filter(Comment.id.in_(descendants)).delete(synchronize_session=False)

    # 3) 부모 댓글 삭제
    db.delete(comment)
    db.commit()
    return comment_id
