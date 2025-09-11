import pytest
from httpx import AsyncClient

from app.models.question import Question
from app.models.user_question import UserQuestion


@pytest.mark.asyncio
async def test_random_question_and_seen_record(client: AsyncClient, token_user1: str):
    # 질문 데이터 시드
    await Question.create(question_text="오늘 나를 가장 웃게 만든 일은?")
    await Question.create(question_text="지금 걱정하는 일은 1년 뒤에도 중요할까?")
    await Question.create(question_text="오늘 나는 무엇을 배웠나?")

    h = {"Authorization": f"Bearer {token_user1}"}

    # 랜덤 질문 1회
    r = await client.get("/api/v1/question/random", headers=h)
    assert r.status_code == 200
    q1 = r.json()
    assert "question_text" in q1 and q1["question_text"]  # ← content → question_text

    # 다시 호출하면 "본 적 없는 질문" 선호
    r = await client.get("/api/v1/question/random", headers=h)
    assert r.status_code == 200
    q2 = r.json()
    assert (
        q1["id"] != q2["id"] or q1["question_text"] != q2["question_text"]
    )  # ← 필드명 수정

    # 3번째 호출
    r = await client.get("/api/v1/question/random", headers=h)
    assert r.status_code == 200
    q3 = r.json()

    # 최소 2개는 서로 달라야 함
    distinct_ids = {q1["id"], q2["id"], q3["id"]}
    assert len(distinct_ids) >= 2

    # UserQuestion 기록이 남는지 간단히 확인
    cnt = await UserQuestion.filter(user_id=1).count()
    assert cnt >= 1
