from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.models.user import User
from app.schemas.bookmark import BookmarkResponse
from app.schemas.quote import QuoteResponse
from app.services.auth_service import get_current_user
from app.services.bookmark_service import (
    svc_add_bookmark,
    svc_list_my_bookmarks,
    svc_remove_bookmark,
)
from app.services.quote_service import (
    svc_get_quote_by_id_or_404,
    svc_get_random_quote,
)

router = APIRouter(prefix="/quote", tags=["quote"])

CurrentUser = Annotated[User, Depends(get_current_user)]


# 1) 랜덤 명언 (인증 필요)
@router.get("/random", response_model=QuoteResponse)
async def get_random_quote(current_user: CurrentUser):
    # 방법 A 적용: 서비스가 _current_user를 받으므로 위치 인자로 전달
    q = await svc_get_random_quote(current_user)
    return QuoteResponse(id=q.id, content=q.content, author=q.author)


# 2) 북마크 추가 (idempotent: 중복이면 200, 새로 만들면 201)
@router.post("/{quote_id}/bookmark", response_model=BookmarkResponse)
async def add_bookmark(quote_id: int, response: Response, current_user: CurrentUser):
    q = await svc_get_quote_by_id_or_404(quote_id)
    bm, created = await svc_add_bookmark(current_user=current_user, quote_id=q.id)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return BookmarkResponse(
        id=bm.id,
        quote=QuoteResponse(id=q.id, content=q.content, author=q.author),
    )


# 3) 북마크 해제 (idempotent)
@router.delete("/{quote_id}/bookmark", status_code=status.HTTP_204_NO_CONTENT)
async def remove_bookmark(quote_id: int, current_user: CurrentUser):
    await svc_remove_bookmark(current_user=current_user, quote_id=quote_id)
    return


# 4) 내 북마크 목록
@router.get("/bookmarks", response_model=list[BookmarkResponse])
async def list_my_bookmarks(
    current_user: CurrentUser,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    items = await svc_list_my_bookmarks(
        current_user=current_user, limit=limit, offset=offset
    )
    out: list[BookmarkResponse] = []
    for bm in items:
        q = bm.quote  # prefetch_related("quote") 덕분에 N+1 방지
        out.append(
            BookmarkResponse(
                id=bm.id,
                quote=QuoteResponse(id=q.id, content=q.content, author=q.author),
            )
        )
    return out
