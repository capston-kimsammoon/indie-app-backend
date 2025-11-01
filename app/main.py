# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.routers import (
    auth, user, search, nearby, venue, alert, like,
    performance, performance_home, calender, artist,
    magazine, review, stamp, review_report , music_magazine
)
from app.routers import notification as notification_router
from app.routers import mood as mood_router
import app.models

app = FastAPI()


# --- Health ---
@app.get("/health")
def health():
    return {"ok": True}


# --- Debug: DB 연결 및 카운트 ---
@app.get("/__debug/db")
def __debug_db():
    with SessionLocal() as db:
        url = str(engine.url)
        try:
            cnt = db.execute(text("SELECT COUNT(*) FROM mood")).scalar()
        except Exception as e:
            cnt = f"ERROR: {e.__class__.__name__}: {e}"
        return {"engine_url": url, "mood_count": cnt}


# --- 정적 파일 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- CORS ---
ALLOW_ORIGINS = [
    "https://modiemodie.com",
    "https://www.modiemodie.com",  # ✅ www 도메인도 허용
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOW_ORIGINS,     # ✅ 반드시 구체 도메인
    allow_credentials=True,          # ✅ 쿠키/세션 사용시 필수
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# --- 라우터 등록 ---
app.include_router(mood_router.router)
app.include_router(mood_router.router, prefix="/performance")  # /performance/mood/* 별칭
app.include_router(performance_home.router)
app.include_router(calender.router)
app.include_router(performance.router)
app.include_router(artist.router)
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
app.include_router(review_report.router)
app.include_router(music_magazine.router, prefix="/musicmagazine")


# --- Root ---
@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
