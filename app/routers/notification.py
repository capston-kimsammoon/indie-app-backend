from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import json

from app.routers import notification as notification_router
from app.database import get_db
from app.utils.dependency import get_current_user
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notification"])
alias = APIRouter(prefix="/notices", tags=["Notification"])
alias.include_router(router)

# ====== Schemas ======
class NotificationRead(BaseModel):
    id: int
    type: str
    title: str
    body: str
    link_url: Optional[str] = None
    is_read: bool
    created_at: datetime
    payload: Optional[Union[Dict[str, Any], List[Any]]] = None

    class Config:
        from_attributes = True

# JSON 파싱 함수 (오류 처리 추가)
def _parse_payload(payload_json: Optional[str]) -> Optional[Union[Dict[str, Any], List[Any]]]:
    if not payload_json:
        return None
    try:
        return json.loads(payload_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format in payload")

# ====== Routes ======
@router.get("", response_model=List[NotificationRead])
def list_notifications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    page: int = Query(1, ge=1),  # 페이지 번호 (1 이상)
    size: int = Query(100, le=100),  # 한 페이지에 표시할 알림 개수 (최대 100)
):
    skip = (page - 1) * size  # 페이징 처리
    rows: List[Notification] = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    return [
        NotificationRead(
            id=n.id,
            type=n.type,
            title=n.title,
            body=n.body,
            link_url=n.link_url,
            is_read=n.is_read,
            created_at=n.created_at,
            payload=_parse_payload(getattr(n, "payload_json", None)),
        ) for n in rows
    ]

@router.patch("/{nid}/read")
def mark_read(nid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(Notification).filter_by(id=nid, user_id=user.id).first()
    if not n:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    db.commit()
    return {"ok": True}

@router.delete("/{nid}")
def remove(nid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(Notification).filter_by(id=nid, user_id=user.id).first()
    if not n:
        raise HTTPException(404, "Notification not found")
    db.delete(n)
    db.commit()
    return {"ok": True}

# === 스케줄/리컨실/강제 트리거 ===
@router.post("/dispatch-due")
def dispatch_due(db: Session = Depends(get_db)):
    from app.services.notify import dispatch_scheduled_notifications
    return dispatch_scheduled_notifications(db)

@router.post("/reconcile-new-performances")
def reconcile_new_performances(hours: int = 72, db: Session = Depends(get_db)):
    from app.services.notify import reconcile_new_performance_notifications
    return reconcile_new_performance_notifications(db, since_hours=hours)

@router.post("/force-new-performance")
def force_new_performance(
    perf_id: int = Query(..., description="performance.id"),
    artist_ids: str = Query(..., description='쉼표 구분, 예: "604" 또는 "600,604"'),
    db: Session = Depends(get_db),
):
    from app.services.notify import notify_artist_followers_on_new_performance
    aid_list = [int(x) for x in artist_ids.split(",") if x.strip()]
    return notify_artist_followers_on_new_performance(db, performance_id=perf_id, artist_ids=aid_list)

@router.post("/dispatch-ticket-open")
def dispatch_ticket_open_now(
    force: bool = Query(False, description="시간 조건 무시하고 강제 발송"),
    pretend_kst: Optional[str] = Query(
        None,
        description="예: 2025-08-23T12:01:00 (이 시간이 현재라고 가정)",
    ),
    db: Session = Depends(get_db),
):
    from app.services.notify import dispatch_scheduled_notifications, KST
    now_utc_override = None
    if pretend_kst:
        # 문자열로 받은 KST 시각을 UTC로 변환해 주입
        dt_kst = datetime.fromisoformat(pretend_kst).replace(tzinfo=KST)
        now_utc_override = dt_kst.astimezone(timezone.utc)

    return dispatch_scheduled_notifications(
        db,
        now_utc_override=now_utc_override,
        force_ticket_open=force,
    )
