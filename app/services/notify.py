# app/services/notify.py
import json
import asyncio
from datetime import datetime, date, time, timedelta, timezone
from typing import Iterable, List, Dict, Optional
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.performance import Performance
from app.models.performance_artist import PerformanceArtist
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.models.user import User
from app.utils.notify import send_expo_push
from app.constants.notification_types import (
    NEW_PERFORMANCE_BY_ARTIST, TICKET_OPEN, FAVORITE_PERFORMANCE_D1
)

KST = timezone(timedelta(hours=9))

# ---------- 내부 유틸 ----------
def _payload_key(perf_id: int) -> str:
    """payload_json과 동일한 직렬화 포맷(키 순서/구분자) 유지"""
    return json.dumps({"performance_id": perf_id}, separators=(",", ":"), ensure_ascii=False)

def _notification_exists(db: Session, *, user_id: int, type_: str, perf_id: Optional[int] = None, payload_json: Optional[str] = None) -> bool:
    """기존 알림 존재 여부 검사 (perf_id 또는 payload_json 방식 모두 지원)"""
    if perf_id is not None:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.type == type_,
            Notification.payload_json == _payload_key(perf_id),
        ).first() is not None
    elif payload_json is not None:
        return db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.type == type_,
            Notification.payload_json == payload_json
        ).first() is not None
    return False

def _kst_noon(d: date) -> datetime:
    """해당 날짜의 12:00 KST"""
    return datetime.combine(d, time(12, 0)).replace(tzinfo=KST)

def _perf_start_kst(perf: Performance) -> datetime:
    """공연 시작 KST (time 없으면 00:00)"""
    return datetime.combine(perf.date, perf.time or time(0, 0)).replace(tzinfo=KST)

def _mk_notification(
    *, user_id: int, type_: str, title: str, body: str,
    link_url: Optional[str], payload: Optional[dict]
) -> Notification:
    return Notification(
        user_id=user_id,
        type=type_,
        title=title,
        body=body,
        link_url=link_url,
        payload_json=json.dumps(payload, separators=(",", ":"), ensure_ascii=False) if payload is not None else None,
        is_read=False,
    )

# ---------- 공개 API ----------
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
    """단건 생성이 꼭 필요할 때 사용."""
    n = _mk_notification(
        user_id=user_id, type_=type_, title=title, body=body,
        link_url=link_url, payload=payload if isinstance(payload, dict) else None
    )
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


def notify_artist_followers_on_new_performance(
    db: Session, *, performance_id: int, artist_ids: Iterable[int]
) -> dict:
    """
    공연 신규 등록 알림(팔로워/알림ON 유저 전원 대상).
    - 중복 알림 방지 포함
    - 대량 insert를 한 번의 commit으로 처리
    """
    artist_ids = sorted(set(artist_ids or []))
    if not artist_ids:
        return {"created": 0, "message": "no artists"}

    # 대상 유저 수집: 찜 + 알림ON
    fav_rows = db.query(UserFavoriteArtist.user_id)\
        .filter(UserFavoriteArtist.artist_id.in_(artist_ids)).distinct().all()
    alarm_rows = db.query(UserArtistTicketAlarm.user_id)\
        .filter(UserArtistTicketAlarm.artist_id.in_(artist_ids)).distinct().all()
    user_ids = sorted({uid for (uid,) in (fav_rows + alarm_rows)})
    if not user_ids:
        return {"created": 0, "message": "no followers"}

    perf = db.query(Performance).filter(Performance.id == performance_id).first()
    if not perf:
        return {"created": 0, "message": "performance not found"}

    payload_str = _payload_key(perf.id)

    # 이미 존재하는 (user, payload) 조합 조회 → 중복 제거
    existed_pairs = {
        (n.user_id, n.payload_json)
        for n in db.query(Notification.user_id, Notification.payload_json)
                   .filter(Notification.type == NEW_PERFORMANCE_BY_ARTIST,
                           Notification.payload_json == payload_str).all()
    }

    to_create: List[Notification] = []
    for uid in user_ids:
        if (uid, payload_str) in existed_pairs:
            continue
        to_create.append(_mk_notification(
            user_id=uid,
            type_=NEW_PERFORMANCE_BY_ARTIST,
            title="새 공연 소식",
            body=f"『{perf.title}』 공연이 등록되었습니다.",
            link_url=f"/performance/{perf.id}",
            payload={"performance_id": perf.id},
        ))

    if to_create:
        db.add_all(to_create)
        db.commit()
        return {"created": len(to_create)}
    return {"created": 0}


def reconcile_new_performance_notifications(db: Session, since_hours: int = 72) -> dict:
    """
    최근 since_hours 시간 내 '생성된 공연'을 스캔하여
    그 공연의 아티스트 팔로워(찜/알림ON)에게 '신공연' 알림을 보충 생성.
    (SQL로 직접 INSERT 한 케이스까지 자동 보정)
    """
    since = datetime.utcnow() - timedelta(hours=since_hours)
    perfs: List[Performance] = db.query(Performance).filter(Performance.created_at >= since).all()
    if not perfs:
        return {"scanned_performances": 0, "created_notifications": 0}

    total_created = 0
    perf_ids = [p.id for p in perfs]
    pa_rows = db.query(PerformanceArtist.performance_id, PerformanceArtist.artist_id)\
                .filter(PerformanceArtist.performance_id.in_(perf_ids)).all()
    artists_by_perf: Dict[int, List[int]] = {}
    for pid, aid in pa_rows:
        artists_by_perf.setdefault(pid, []).append(aid)

    to_create_bulk: List[Notification] = []

    for p in perfs:
        artist_ids = artists_by_perf.get(p.id, [])
        if not artist_ids:
            continue

        fav_users = [uid for (uid,) in db.query(UserFavoriteArtist.user_id)
                     .filter(UserFavoriteArtist.artist_id.in_(artist_ids)).distinct().all()]
        alarm_users = [uid for (uid,) in db.query(UserArtistTicketAlarm.user_id)
                       .filter(UserArtistTicketAlarm.artist_id.in_(artist_ids)).distinct().all()]
        user_ids = list(set(fav_users) | set(alarm_users))
        if not user_ids:
            continue

        payload_str = _payload_key(p.id)
        existed_pairs = {
            (n.user_id, n.payload_json)
            for n in db.query(Notification.user_id, Notification.payload_json)
                       .filter(Notification.type == NEW_PERFORMANCE_BY_ARTIST,
                               Notification.payload_json == payload_str).all()
        }

        for uid in user_ids:
            if (uid, payload_str) in existed_pairs:
                continue
            to_create_bulk.append(_mk_notification(
                user_id=uid,
                type_=NEW_PERFORMANCE_BY_ARTIST,
                title="새 공연 소식",
                body=f"『{p.title}』 공연이 등록되었습니다.",
                link_url=f"/performance/{p.id}",
                payload={"performance_id": p.id},
            ))

    if to_create_bulk:
        db.add_all(to_create_bulk)
        db.commit()
        total_created = len(to_create_bulk)

    return {"scanned_performances": len(perfs), "created_notifications": total_created}


# ---------- 통합 Dispatch (DB 알림 + 푸시 전송) ----------
def dispatch_scheduled_notifications(db: Session, *, now_utc_override: Optional[datetime] = None) -> dict:
    """DB 알림 생성 + Expo Push 전송까지 한 번에 처리"""

    now_utc = (now_utc_override or datetime.utcnow()).replace(tzinfo=timezone.utc)

    # (1) 예매오픈 알림
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

    # (2) 공연 D-1 알림
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

    # (3) Expo Push 전송
    async def _send_push(notifications: List[Notification]):
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
