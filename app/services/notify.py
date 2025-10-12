from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
import asyncio

from app.models.notification import Notification
from app.models.performance import Performance
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.models.user_favorite_performance import UserFavoritePerformance
from app.utils.notify import send_expo_push
from app.constants.notification_types import TICKET_OPEN, FAVORITE_PERFORMANCE_D1

KST = timezone(timedelta(hours=9))

# ---------- 기존 헬퍼 ----------
def _perf_start_kst(perf: Performance) -> datetime:
    return datetime.combine(perf.date, perf.time or time(0, 0)).replace(tzinfo=KST)

def _mk_notification(*, user_id: int, type_: str, title: str, body: str, link_url: str, payload: dict) -> Notification:
    from app.models.user import User
    return Notification(
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
        link_url=link_url,
        payload_json=json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
        is_read=False
    )

def _notification_exists(db: Session, *, user_id: int, type_: str, payload_json: str) -> bool:
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.type == type_,
        Notification.payload_json == payload_json
    ).first() is not None

# ---------- 통합 dispatch ----------
def dispatch_scheduled_notifications(db: Session, *, now_utc_override: Optional[datetime] = None) -> dict:
    """DB 알림 생성 + 푸시 전송까지 통합"""

    now_utc = (now_utc_override or datetime.utcnow()).replace(tzinfo=timezone.utc)

    # ---------- (1) 예매오픈 ----------
    open_rows = db.query(UserPerformanceTicketAlarm.user_id, UserPerformanceTicketAlarm.performance_id).all()
    to_create_open: List[Notification] = []
    perf_cache: Dict[int, Performance] = {}

    def _get_perf(pid: int) -> Optional[Performance]:
        if pid not in perf_cache:
            perf_cache[pid] = db.query(Performance).filter(Performance.id == pid).first()
        return perf_cache[pid]

    for uid, pid in open_rows:
        perf = _get_perf(pid)
        if not perf or not perf.ticket_open_date:
            continue
        due_utc = datetime.combine(perf.ticket_open_date - timedelta(days=1), time(12, 0), tzinfo=KST).astimezone(timezone.utc)
        if now_utc < due_utc:
            continue

        payload = {"performance_id": pid}
        payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        if _notification_exists(db, user_id=uid, type_=TICKET_OPEN, payload_json=payload_json):
            continue

        to_create_open.append(_mk_notification(
            user_id=uid,
            type_=TICKET_OPEN,
            title="예매 오픈 알림",
            body=f"『{perf.title}』 예매가 곧 열립니다.",
            link_url=f"/performance/{perf.id}",
            payload=payload,
        ))

    if to_create_open:
        db.add_all(to_create_open)
        db.commit()

    # ---------- (2) 공연찜 D-1 ----------
    fav_rows = db.query(UserFavoritePerformance.user_id, UserFavoritePerformance.performance_id).all()
    to_create_fav: List[Notification] = []

    for uid, pid in fav_rows:
        perf = _get_perf(pid)
        if not perf or not perf.date:
            continue
        due_utc = datetime.combine(perf.date - timedelta(days=1), time(12, 0), tzinfo=KST).astimezone(timezone.utc)
        if now_utc < due_utc:
            continue

        payload = {"performance_id": pid}
        payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
        if _notification_exists(db, user_id=uid, type_=FAVORITE_PERFORMANCE_D1, payload_json=payload_json):
            continue

        to_create_fav.append(_mk_notification(
            user_id=uid,
            type_=FAVORITE_PERFORMANCE_D1,
            title="공연 D-1 알림",
            body=f"『{perf.title}』 공연이 내일입니다.",
            link_url=f"/performance/{perf.id}",
            payload=payload,
        ))

    if to_create_fav:
        db.add_all(to_create_fav)
        db.commit()

    # ---------- (3) 푸시 전송 ----------
    async def _send_push(notifications: List[Notification]):
        from app.models.user import User
        tasks = []
        for n in notifications:
            user = db.query(User).filter(User.id == n.user_id).first()
            if user and user.alarm_enabled and user.push_token:
                tasks.append(send_expo_push(
                    token=user.push_token,
                    title=n.title,
                    body=n.body,
                    payload={"nid": n.id}
                ))
        if tasks:
            await asyncio.gather(*tasks)

    asyncio.run(_send_push(to_create_open + to_create_fav))

    return {
        "created_ticket_open": len(to_create_open),
        "created_favorite_d1": len(to_create_fav),
    }
