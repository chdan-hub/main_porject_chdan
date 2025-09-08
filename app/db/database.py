import os

from dotenv import load_dotenv
from tortoise import Tortoise

# .env 파일에서 환경 변수 로드
load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB")

# 데이터베이스 URL 생성
db_url = f"postgres://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

TORTOISE_ORM = {
    "connections": {
        "default": db_url  # 여기서 정의한 db_url 사용
    },
    "apps": {
        "models": {
            "models": [
                "app.models.user",
                "app.models.token_blacklist",
                "app.models.diary",
                "app.models.quote",
                "app.models.bookmark",
                "app.models.question",
                "app.models.user_question",
                "aerich.models",
            ],
            "default_connection": "default",
        }
    },
}


async def init_db():
    """
    Tortoise ORM으로 DB 연결 초기화 및 스키마 생성
    """
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        await Tortoise.generate_schemas()
        print("✅ 데이터베이스 연결 및 스키마 생성 완료")
    except Exception as e:
        print(f"데이터베이스 연결 초기화 실패: {e}")
