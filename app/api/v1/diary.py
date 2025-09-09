# 일기 API

from fastapi import APIRouter

router = APIRouter(prefix="/diary", tags=["diary"])


# 최소 헬스체크 엔드포인트 (프로젝트 부팅 검증용)
@router.get("/health")
async def diary_health():
    return {"ok": True}
