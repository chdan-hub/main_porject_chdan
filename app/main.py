from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 프로젝트의 API 라우터들을 임포트합니다.
from app.api.v1 import auth, diary, question, quote
from app.core.config import settings

# 사용자 기존의 database.py 파일에서 init_db 함수를 임포트
from app.db.database import init_db

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)


# DB 연결 및 초기화
@app.on_event("startup")
async def startup_event():
    print("DB 연결 중...")
    await init_db()
    print("DB 연결 완료")


# CORS 미들웨어 추가: 프론트엔드와 백엔드 간 통신을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 환경에서는 특정 도메인만 허용하는 것이 좋습니다.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함: 각 기능별 API 엔드포인트를 등록합니다.
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(diary.router, prefix=settings.API_V1_STR)
app.include_router(quote.router, prefix=settings.API_V1_STR)
app.include_router(question.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {"message": "Welcome to my private diary API!"}
