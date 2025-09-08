# app/db/database.py

import os

from dotenv import load_dotenv
from tortoise import Tortoise

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# 마이그레이션이 필요한 모델 리스트
TORTOISE_MODELS = [
    "app.models.user",
    "aerich.models"  # <-- 이 줄을 추가합니다.
]

# Aerich가 인식할 Tortoise ORM 설정 딕셔너리
TORTOISE_CONFIG = {
    "connections": {"default": f"postgres://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"},
    "apps": {
        "models": {
            "models": TORTOISE_MODELS,
            "default_connection": "default",
        }
    }
}

async def init_db():
    """
    Tortoise ORM을 사용하여 데이터베이스 연결을 초기화합니다.
    """
    try:
        await Tortoise.init(config=TORTOISE_CONFIG)
        print("🎉 데이터베이스에 성공적으로 연결되었습니다!")
        # 실제 배포 환경에서는 마이그레이션 도구(Aerich)를 사용해야 합니다.
        # 개발 시 자동 스키마 생성이 필요한 경우에만 아래 주석을 해제하세요.
        # await Tortoise.generate_schemas()
    except Exception as e:
        print(f"❌ 데이터베이스 연결에 실패했습니다: {e}")