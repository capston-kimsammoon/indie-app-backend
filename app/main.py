from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import asyncio
from contextlib import suppress
from sqlalchemy import text

from app.database import SessionLocal, Base, engine
from app.routers import (
    auth, user, search, nearby, venue, alert, like,
    performance, performance_home, calender, artist,
    magazine, review, stamp
)
from app.routers import notification as notification_router
from app.routers import mood as mood_router
import app.models

# ✅ FastAPI 앱 초기화
app = FastAPI()

# ✅ 👉 헬스 체크 엔드포인트 (app 선언 바로 아래에 둡니다)
@app.get("/health")
def health():
    return {"ok": True}

@app.get("/__debug/db")
def __debug_db():
    from app.database import SessionLocal, engine
    with SessionLocal() as db:
        url = str(engine.url)
        try:
            cnt = db.execute(text("SELECT COUNT(*) FROM mood")).scalar()
        except Exception as e:
            cnt = f"ERROR: {e.__class__.__name__}: {e}"
        return {"engine_url": url, "mood_count": cnt}

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

# ✅ 라우터 등록
app.include_router(mood_router.router)
app.include_router(mood_router.router, prefix="/performance")
app.include_router(performance_home.router)
app.include_router(calender.router)
app.include_router(performance.router)
app.include_router(artist.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(search.router)
app.include_router(nearby.router)
app.include_router(review.router)
app.include_router(venue.router)
app.include_router(alert.router)
app.include_router(like.router)
app.include_router(magazine.router)
app.include_router(notification_router.router)
app.include_router(notification_router.alias)
app.include_router(stamp.router)

# ✅ 루트 엔드포인트
@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}