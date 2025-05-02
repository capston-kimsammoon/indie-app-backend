from fastapi import FastAPI
from app import models
from .database import engine
from app.database import Base


app = FastAPI()

# DB 테이블 생성
Base.metadata.create_all(bind=engine)  # 테이블 생성


@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
