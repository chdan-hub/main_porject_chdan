# tests/conftest.py
import os
from contextlib import asynccontextmanager

import pytest
from asgi_lifespan import LifespanManager  # ★ 추가
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

# 테스트 전에 기본 환경변수(SECRET_KEY 등) 보정
os.environ.setdefault("SECRET_KEY", "test-secret")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

# 라우터 임포트
from app.api.v1 import auth, diary, question, quote  # noqa: E402

TEST_TORTOISE_ORM = {
    "connections": {"default": "sqlite://:memory:"},
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
            ],
            "default_connection": "default",
        }
    },
}


# ★ lifespan으로 DB init/close
@asynccontextmanager
async def lifespan(_app: FastAPI):
    await Tortoise.init(config=TEST_TORTOISE_ORM)
    await Tortoise.generate_schemas()
    try:
        yield
    finally:
        await Tortoise.close_connections()


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(diary.router, prefix="/api/v1")
    app.include_router(quote.router, prefix="/api/v1")
    app.include_router(question.router, prefix="/api/v1")
    return app


@pytest.fixture
async def client(test_app: FastAPI):
    # ★ LifespanManager로 startup/shutdown 보장
    async with LifespanManager(test_app):
        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


# ----- 테스트 헬퍼 -----
async def _register_and_login(
    client: AsyncClient, username="alice", email=None, password="secret123!"
):
    email = email or f"{username}@example.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"username": username, "email": email, "password": password},
    )
    assert r.status_code == 201, r.text

    r = await client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
async def token_user1(client: AsyncClient):
    return await _register_and_login(client, "alice", "alice@example.com")


@pytest.fixture
async def token_user2(client: AsyncClient):
    return await _register_and_login(client, "bob", "bob@example.com")
