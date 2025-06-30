# app/main.py

from fastapi import FastAPI
from app.routers import artist_router

app = FastAPI()

app.include_router(artist_router.router)

@app.get("/")
def root():
    return {"message": "FastAPI 서비스 동작 중"}
