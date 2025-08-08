from fastapi import FastAPI
from app import models 
from app.database import Base, engine

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
app = FastAPI()

# Alembic 사용 시 x
# Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.routers import (post, auth, user, search, nearby, venue, alert, like, performance, performance_home, calender, artist, comment )
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# 라우터 등록
app.include_router(user.router)
app.include_router(post.router)
app.include_router(performance_home.router)
app.include_router(calender.router)
app.include_router(performance.router)
app.include_router(artist.router)
app.include_router(comment.router)
app.include_router(auth.router)

app.include_router(search.router)
app.include_router(nearby.router)
app.include_router(venue.router)
app.include_router(alert.router)
app.include_router(like.router)

@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
