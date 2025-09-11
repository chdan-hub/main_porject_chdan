# tests/test_diary.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_diary_crud_and_permissions(
    client: AsyncClient, token_user1: str, token_user2: str
):
    h1 = {"Authorization": f"Bearer {token_user1}"}
    h2 = {"Authorization": f"Bearer {token_user2}"}

    # 생성
    r = await client.post(
        "/api/v1/diary",
        json={"title": "first", "content": "hello world"},
        headers=h1,
    )
    assert r.status_code in (200, 201)
    d = r.json()
    diary_id = d["id"]

    # 조회
    r = await client.get(f"/api/v1/diary/{diary_id}", headers=h1)
    assert r.status_code == 200
    assert r.json()["title"] == "first"

    # 수정(작성자 OK)
    r = await client.put(
        f"/api/v1/diary/{diary_id}",
        json={"title": "first-edit", "content": "updated"},
        headers=h1,
    )
    assert r.status_code == 200
    assert r.json()["title"] == "first-edit"

    # 다른 사용자 수정 → 403
    r = await client.put(
        f"/api/v1/diary/{diary_id}",
        json={"title": "hacked", "content": "nope"},
        headers=h2,
    )
    assert r.status_code in (403, 404)  # 구현에 따라 403 또는 404

    # 목록 (내 글만)
    r = await client.get("/api/v1/diary/my?limit=10&offset=0", headers=h1)
    assert r.status_code == 200
    items = r.json()
    assert any(item["id"] == diary_id for item in items)

    # 삭제(작성자 OK)
    r = await client.delete(f"/api/v1/diary/{diary_id}", headers=h1)
    assert r.status_code in (200, 204)

    # 다시 조회 → 404
    r = await client.get(f"/api/v1/diary/{diary_id}", headers=h1)
    assert r.status_code == 404
