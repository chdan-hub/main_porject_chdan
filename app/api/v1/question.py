# 질문 API

from fastapi import APIRouter

router = APIRouter(prefix="/question", tags=["question"])


@router.get("/health")
async def question_health():
    return {"ok": True}
