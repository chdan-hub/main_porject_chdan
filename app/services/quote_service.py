from fastapi import HTTPException, status

from app.models.quote import Quote
from app.models.user import User
from app.repositories.quote_repo import get_quote_by_id, get_random_quote


# 인증 컨텍스트 보장을 위해 인자를 받지만, 내부에서 사용하지 않습니다.
async def svc_get_random_quote(_current_user: User) -> Quote:  # noqa: ARG001
    q = await get_random_quote()
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="명언 데이터가 없습니다."
        )
    return q


async def svc_get_quote_by_id_or_404(quote_id: int) -> Quote:
    q = await get_quote_by_id(quote_id)
    if not q:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="명언을 찾을 수 없습니다."
        )
    return q
