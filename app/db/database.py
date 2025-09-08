import os

from dotenv import load_dotenv
from tortoise import Tortoise

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 마이그레이션이 필요한 모든 모델 리스트
TORTOISE_MODELS = [
    "app.models.user",
    "app.models.token_blacklist",
    "app.models.diary",
    "app.models.quote",
    "app.models.bookmark",
    "app.models.question",
    "app.models.user_question",
    "aerich.models",
]

# Aerich가 인식할 Tortoise ORM 설정 딕셔너리
TORTOISE_CONFIG = {
    "connections": {
        "default": f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
    },
    "apps": {
        "models": {
            "models": TORTOISE_MODELS,
            "default_connection": "default",
        }
    },
}


def get_database_url():
    """
    .env 파일의 환경 변수를 사용하여 데이터베이스 URL을 구성합니다.
    """
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")

    return f"postgres://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


async def init_db():
    """
    Tortoise ORM을 사용하여 데이터베이스 연결을 초기화하고
    마이그레이션이 필요없는 경우 즉시 스키마를 생성합니다.
    """
    try:
        await Tortoise.init(config=TORTOISE_CONFIG)
        await Tortoise.generate_schemas()
    except Exception as e:
        print(f"데이터베이스 연결 초기화 실패: {e}")
