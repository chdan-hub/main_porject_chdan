from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.diary_repo import (
    create_diary,
    delete_diary,
    get_diary_by_id_for_user,
    list_diaries_for_user,
    update_diary_fields,
)


async def svc_create_diary(*, current_user: User, title: str, content: str):
    return await create_diary(user=current_user, title=title, content=content)


async def svc_list_my_diaries(*, current_user: User, limit: int = 20, offset: int = 0):
    return await list_diaries_for_user(current_user.id, limit=limit, offset=offset)


async def svc_get_my_diary(*, current_user: User, diary_id: int):
    diary = await get_diary_by_id_for_user(diary_id, current_user.id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다."
        )
    return diary


async def svc_update_my_diary(
    *, current_user: User, diary_id: int, title=None, content=None
):
    diary = await get_diary_by_id_for_user(diary_id, current_user.id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다."
        )
    return await update_diary_fields(diary, title=title, content=content)


async def svc_delete_my_diary(*, current_user: User, diary_id: int):
    diary = await get_diary_by_id_for_user(diary_id, current_user.id)
    if not diary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="일기를 찾을 수 없습니다."
        )
    await delete_diary(diary)
