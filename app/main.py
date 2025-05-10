# app/main.py
from fastapi import FastAPI
from app import models
from .database import engine
from app.database import Base
from .services.instagram.info_extractor import extract_performance_info
from .services.instagram.get_post import get_posts_from_all_accounts

app = FastAPI()

# DB 테이블 생성
# Base.metadata.create_all(bind=engine)  # 테이블 생성

@app.get("/")
def root():
    # get_posts_from_all_accounts()
    return {"message": "MySQL 테이블 생성 완료 !!"}
