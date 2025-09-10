from typing import Iterable, Optional

from app.models.diary import Diary
from app.models.user import User


async def create_diary(*, user: User, title: str, content: str) -> Diary:
    return await Diary.create(user=user, title=title, content=content)


async def get_diary_by_id_for_user(diary_id: int, user_id: int) -> Optional[Diary]:
    # Tortoise는 FK 필드에 *_id 속성을 제공합니다.
    return await Diary.get_or_none(id=diary_id, user_id=user_id)


async def list_diaries_for_user(
    user_id: int, *, limit: int = 20, offset: int = 0
) -> Iterable[Diary]:
    return (
        await Diary.filter(user_id=user_id)
        .order_by("-created_at")
        .offset(offset)
        .limit(limit)
    )


async def update_diary_fields(
    diary: Diary, *, title: str | None = None, content: str | None = None
) -> Diary:
    if title is not None:
        diary.title = title
    if content is not None:
        diary.content = content
    await diary.save()
    return diary


async def delete_diary(diary: Diary) -> None:
    await diary.delete()
