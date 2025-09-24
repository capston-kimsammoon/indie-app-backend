# app/main.py
import os
import asyncio
from contextlib import suppress

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import SessionLocal, Base, engine
from app.routers import (
    post, auth, user, search, nearby, venue, alert, like,
    performance, performance_home, calender, artist, comment,
    magazine, review, stamp
)


from app.routers import notification as notification_router
from app.routers import mood as mood_router 
import app.models

# ✅ FastAPI 앱 초기화
app = FastAPI()

# ✅ 정적 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ✅ CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 라우터 등록 (⚠️ 정적 경로를 먼저: /performance/mood → /performance/{id} 충돌 방지)
app.include_router(mood_router.router)                          # /mood/...
app.include_router(mood_router.router, prefix="/performance")   # /performance/mood/...

app.include_router(post.router)
app.include_router(performance_home.router)
app.include_router(calender.router)
app.include_router(performance.router)          # ← 파라미터 라우트는 mood 별칭 뒤에 등록
app.include_router(artist.router)
app.include_router(comment.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(search.router)
app.include_router(nearby.router)
app.include_router(venue.router)
app.include_router(alert.router)
app.include_router(like.router)
app.include_router(magazine.router)             
app.include_router(notification_router.router)  
app.include_router(notification_router.alias)   
app.include_router(review.router)
app.include_router(stamp.router)


# ✅ 알림 라우터 (신규 + 레거시 호환 둘 다)
app.include_router(notification_router.router)   # /notifications/*
app.include_router(notification_router.alias)    # /notices/notifications/*


# ✅ 루트 엔드포인트
@app.get("/")
def root():
   
    return {"message": "MySQL 테이블 생성 완료 !!"}

# === 백그라운드 루프: SQL 직삽도 자동 반영 ===
async def _loop_reconcile_new_perfs():
    from app.services.notify import reconcile_new_performance_notifications
    while True:
        with suppress(Exception):
            db = SessionLocal()
            try:
                # 최근 24시간치만 스캔 → 1분마다 갱신
                reconcile_new_performance_notifications(db, since_hours=24)
            finally:
                db.close()
        await asyncio.sleep(60)  # 1분마다

async def _loop_ticket_open():
    from app.services.notify import dispatch_scheduled_notifications
    while True:
        with suppress(Exception):
            db = SessionLocal()
            try:
                dispatch_scheduled_notifications(db)
            finally:
                db.close()
        await asyncio.sleep(60)  # 1분마다

@app.on_event("startup")
async def _startup_loops():
    # 서버 켜지면 자동으로 두 루프 시작
    asyncio.create_task(_loop_reconcile_new_perfs())
    asyncio.create_task(_loop_ticket_open())
