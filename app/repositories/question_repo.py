import random
from typing import Optional

from app.models.question import Question
from app.models.user_question import UserQuestion


async def get_random_question() -> Optional[Question]:
    """
    전체에서 랜덤 1건.
    """
    count = await Question.all().count()
    if count == 0:
        return None
    offset = random.randint(0, count - 1)
    return await Question.all().offset(offset).limit(1).first()


async def get_random_unseen_question_for_user(user_id: int) -> Optional[Question]:
    """
    사용자가 '본 기록'이 없는 질문 중 랜덤 1건.
    없으면 None.
    """
    seen_ids = await UserQuestion.filter(user_id=user_id).values_list(
        "question_id", flat=True
    )
    qs = Question.exclude(id__in=seen_ids)
    count = await qs.count()
    if count == 0:
        return None
    offset = random.randint(0, count - 1)
    return await qs.offset(offset).limit(1).first()
