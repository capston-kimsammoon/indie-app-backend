from fastapi import FastAPI
from app import models  # ✅ 반드시 먼저 import
from app.database import Base, engine
from app.routers import post

app = FastAPI()

# Alembic 사용 시 x
# Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(post.router)

@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
