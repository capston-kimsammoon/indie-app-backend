# app/services/notify.py
import json
from datetime import datetime, date, time, timedelta, timezone
from typing import Iterable

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.performance import Performance
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.models.user_performance_open_alarm import UserPerformanceOpenAlarm
from app.models.user_favorite_performance import UserFavoritePerformance


KST = timezone(timedelta(hours=9))


def _notification_exists(db: Session, *, user_id: int, type_: str, perf_id: int) -> bool:
    """동일 사용자/타입/공연에 대한 알림이 이미 있는지 payload_json 기준으로 중복 방지."""
    payload_key = json.dumps({"performance_id": perf_id}, separators=(",", ":"), ensure_ascii=False)
    return db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.type == type_,
        Notification.payload_json == payload_key,
    ).first() is not None


def create_notification(
    db: Session,
    *,
    user_id: int,
    type_: str,
    title: str,
    body: str,
    link_url: str | None = None,
    payload: dict | list | None = None,
) -> Notification:
    n = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
        link_url=link_url,
        payload_json=json.dumps(payload, separators=(",", ":"), ensure_ascii=False) if payload is not None else None,
        is_read=False,
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def notify_artist_followers_on_new_performance(
    db: Session, *, performance_id: int, artist_ids: Iterable[int]
) -> dict:
    """아티스트 알림(팔로우) 켜 둔 사용자에게 '새 공연' 알림 생성."""
    artist_ids = list(artist_ids) or []
    if not artist_ids:
        return {"created": 0, "message": "no artists"}

    # 알림 대상 사용자 id 목록
    user_rows = (
        db.query(UserArtistTicketAlarm.user_id)
        .filter(UserArtistTicketAlarm.artist_id.in_(artist_ids))
        .distinct()
        .all()
    )
    user_ids = [uid for (uid,) in user_rows]
    if not user_ids:
        return {"created": 0, "message": "no followers"}

    perf = db.query(Performance).filter(Performance.id == performance_id).first()
    if not perf:
        return {"created": 0, "message": "performance not found"}

    created = 0
    for uid in user_ids:
        if _notification_exists(db, user_id=uid, type_="new_performance_by_artist", perf_id=perf.id):
            continue
        create_notification(
            db,
            user_id=uid,
            type_="new_performance_by_artist",
            title="새 공연 소식",
            body=f"『{perf.title}』 공연이 등록되었습니다.",
            link_url=f"/performance/{perf.id}",
            payload={"performance_id": perf.id},
        )
        created += 1
    return {"created": created}


def _kst_noon(d: date) -> datetime:
    """해당 날짜 KST 정오(12:00) → aware datetime(KST)."""
    return datetime.combine(d, time(12, 0)).replace(tzinfo=KST)


def dispatch_scheduled_notifications(db: Session) -> dict:
    """
    - 예매오픈 알림(ticket_open): ticket_open_date의 '전날 12:00(KST)'
    - 공연찜 D-1 알림(favorite_performance_d1): performance.date의 '전날 12:00(KST)'
    """
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)

    # 1) 예매오픈 알림: 해당 공연에 대해 ticket_open 알림 ON 한 사용자
    open_rows = (
        db.query(UserPerformanceOpenAlarm.user_id, UserPerformanceOpenAlarm.performance_id)
        .all()
    )
    created_open = 0
    for uid, pid in open_rows:
        perf = db.query(Performance).filter(Performance.id == pid).first()
        if not perf or not perf.ticket_open_date:
            continue

        due_kst = _kst_noon(perf.ticket_open_date - timedelta(days=1))
        due_utc = due_kst.astimezone(timezone.utc)
        if now_utc >= due_utc:
            if _notification_exists(db, user_id=uid, type_="ticket_open", perf_id=pid):
                continue
            create_notification(
                db,
                user_id=uid,
                type_="ticket_open",
                title="예매 오픈 알림",
                body=f"『{perf.title}』 예매가 곧 열립니다.",
                link_url=f"/performance/{perf.id}",
                payload={"performance_id": perf.id},
            )
            created_open += 1

    # 2) 공연찜 D-1 알림: 사용자-공연 찜한 경우
    fav_rows = (
        db.query(UserFavoritePerformance.user_id, UserFavoritePerformance.performance_id)
        .all()
    )
    created_fav = 0
    for uid, pid in fav_rows:
        perf = db.query(Performance).filter(Performance.id == pid).first()
        if not perf or not perf.date:
            continue

        due_kst = _kst_noon(perf.date - timedelta(days=1))
        due_utc = due_kst.astimezone(timezone.utc)
        if now_utc >= due_utc:
            if _notification_exists(db, user_id=uid, type_="favorite_performance_d1", perf_id=pid):
                continue
            create_notification(
                db,
                user_id=uid,
                type_="favorite_performance_d1",
                title="공연 D-1 알림",
                body=f"『{perf.title}』 공연이 내일입니다.",
                link_url=f"/performance/{perf.id}",
                payload={"performance_id": perf.id},
            )
            created_fav += 1

    return {"created_ticket_open": created_open, "created_favorite_d1": created_fav}
