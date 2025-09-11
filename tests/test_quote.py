# tests/test_quote.py
import pytest
from httpx import AsyncClient

from app.models.quote import Quote


@pytest.mark.asyncio
async def test_random_quote_and_bookmark_flow(client: AsyncClient, token_user1: str):
    # 테스트용 명언 1개 이상 준비
    await Quote.create(content="Stay hungry, stay foolish.", author="Steve Jobs")

    h = {"Authorization": f"Bearer {token_user1}"}

    # 랜덤 명언
    r = await client.get("/api/v1/quote/random", headers=h)
    assert r.status_code == 200
    q = r.json()
    assert "content" in q and q["content"]

    quote_id = q["id"]

    # 북마크 추가 (처음: 201, 다시: 200)
    r = await client.post(f"/api/v1/quote/{quote_id}/bookmark", headers=h)
    assert r.status_code in (200, 201)
    first_status = r.status_code

    r = await client.post(f"/api/v1/quote/{quote_id}/bookmark", headers=h)
    assert r.status_code == (200 if first_status == 201 else 201)

    # 북마크 목록
    r = await client.get("/api/v1/quote/bookmarks", headers=h)
    assert r.status_code == 200
    items = r.json()
    assert any(bm["quote"]["id"] == quote_id for bm in items)

    # 북마크 해제 (idempotent)
    r = await client.delete(f"/api/v1/quote/{quote_id}/bookmark", headers=h)
    assert r.status_code == 204
    r = await client.delete(f"/api/v1/quote/{quote_id}/bookmark", headers=h)
    assert r.status_code == 204

    # 목록 비어있는지 확인(또는 해당 quote 없어졌는지)
    r = await client.get("/api/v1/quote/bookmarks", headers=h)
    assert r.status_code == 200
    items = r.json()
    assert not any(bm["quote"]["id"] == quote_id for bm in items)
