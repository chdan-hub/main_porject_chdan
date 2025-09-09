# 명언 API

from fastapi import APIRouter

router = APIRouter(prefix="/quote", tags=["quote"])


@router.get("/health")
async def quote_health():
    return {"ok": True}
