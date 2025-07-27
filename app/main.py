from fastapi import FastAPI
from app import models  # ✅ 반드시 먼저 import
from app.database import Base, engine

app = FastAPI()

# ✅ 이 시점에서 모든 모델이 로딩되었어야 함!
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
