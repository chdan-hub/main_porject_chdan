from typing import Tuple

from app.models.bookmark import Bookmark
from app.models.user import User
from app.repositories.bookmark_repo import (
    create_bookmark,
    delete_bookmark,
    get_bookmark_by_user_and_quote,
    list_bookmarks_for_user,
)


async def svc_add_bookmark(
    *, current_user: User, quote_id: int
) -> Tuple[Bookmark, bool]:
    """
    반환: (bookmark, created)
    created=True면 새로 생성, False면 기존 북마크(중복 방지)
    """
    existing = await get_bookmark_by_user_and_quote(current_user.id, quote_id)
    if existing:
        return existing, False
    bm = await create_bookmark(current_user.id, quote_id)
    return bm, True


async def svc_remove_bookmark(*, current_user: User, quote_id: int) -> None:
    await delete_bookmark(current_user.id, quote_id)


async def svc_list_my_bookmarks(
    *, current_user: User, limit: int = 50, offset: int = 0
) -> list[Bookmark]:
    return await list_bookmarks_for_user(current_user.id, limit=limit, offset=offset)
