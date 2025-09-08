# app/main.py

from fastapi import FastAPI

from app.db.database import init_db

app = FastAPI()

# 애플리케이션 시작 시 데이터베이스 연결 초기화
@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
def read_root():
    return {"Hello": "World"}