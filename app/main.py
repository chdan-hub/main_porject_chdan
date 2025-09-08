# app/main.py

from fastapi import FastAPI

from app.db.database import init_db

app = FastAPI()


@app.on_event("startup")
async def on_startup():
    # 앱 시작 시 DB 초기화
    await init_db()


@app.get("/")
def read_root():
    return {"Hello": "World"}
