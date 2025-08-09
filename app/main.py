from fastapi import FastAPI
from app import models
from app.database import Base, engine
from app.routers import (
    post, auth, user, search, nearby, venue, alert, like,
    performance, performance_home, calender, artist, comment
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# ✅ FastAPI 앱 초기화
app = FastAPI()

# ✅ 정적 파일 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ✅ 프론트엔드 출처
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

# ✅ CORS 미들웨어 (기본 설정)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # '*' 대신 명시적 도메인
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 라우터 등록
app.include_router(post.router)
app.include_router(performance_home.router)
app.include_router(calender.router)
app.include_router(performance.router)
app.include_router(artist.router)
app.include_router(comment.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(search.router)
app.include_router(nearby.router)
app.include_router(venue.router)
app.include_router(alert.router)
app.include_router(like.router)

# ✅ 루트 엔드포인트
@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
