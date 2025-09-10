from fastapi import HTTPException, status

from app.models.question import Question
from app.models.user import User
from app.models.user_question import UserQuestion
from app.repositories.question_repo import (
    get_random_question,
    get_random_unseen_question_for_user,
)


# 인증 컨텍스트를 받지만 내부에서 변수는 사용하지 않습니다.
async def svc_get_random_question(_current_user: User) -> Question:  # noqa: ARG001
    # 1) 본 적 없는 질문을 우선 제공
    q = await get_random_unseen_question_for_user(_current_user.id)
    # 2) 모두 본 상태면 아무거나 랜덤
    if not q:
        q = await get_random_question()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="질문 데이터가 없습니다."
        )

    # 본 것으로 기록(중복 기록 방지)
    await UserQuestion.get_or_create(
        user_id=_current_user.id,
        question_id=q.id,
        defaults={"seen": True},
    )
    return q
