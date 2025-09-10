from typing import Optional

from app.models.bookmark import Bookmark


async def get_bookmark_by_user_and_quote(
    user_id: int, quote_id: int
) -> Optional[Bookmark]:
    return await Bookmark.get_or_none(user_id=user_id, quote_id=quote_id)


async def create_bookmark(user_id: int, quote_id: int) -> Bookmark:
    # DB unique_together로도 막히지만, 애플리케이션 레벨에서 선제 체크
    existing = await get_bookmark_by_user_and_quote(user_id, quote_id)
    if existing:
        return existing
    return await Bookmark.create(user_id=user_id, quote_id=quote_id)


async def delete_bookmark(user_id: int, quote_id: int) -> None:
    await Bookmark.filter(user_id=user_id, quote_id=quote_id).delete()


async def list_bookmarks_for_user(
    user_id: int, *, limit: int = 50, offset: int = 0
) -> list[Bookmark]:
    return (
        await Bookmark.filter(user_id=user_id)
        .prefetch_related("quote")
        .order_by("-id")
        .offset(offset)
        .limit(limit)
    )
