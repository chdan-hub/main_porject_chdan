# tests/test_auth.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_me_logout(client: AsyncClient):
    # 회원가입
    r = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "jane",
            "email": "jane@example.com",
            "password": "secret123!",
        },
    )
    assert r.status_code == 201
    assert r.json()["username"] == "jane"

    # 중복 가입(이메일) 실패
    r2 = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "jane2",
            "email": "jane@example.com",
            "password": "secret123!",
        },
    )
    assert r2.status_code == 400

    # 로그인(이름으로)
    r = await client.post(
        "/api/v1/auth/login",
        data={"username": "jane", "password": "secret123!"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    token = r.json()["access_token"]

    # me
    r = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["username"] == "jane"
    assert data["email"] == "jane@example.com"

    # 로그아웃
    r = await client.post(
        "/api/v1/auth/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 204

    # 로그아웃된 토큰으로 me → 401
    r = await client.get(
        "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 401
