from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.user import User
from app.schemas.question import QuestionResponse
from app.services.auth_service import get_current_user
from app.services.question_service import svc_get_random_question

router = APIRouter(prefix="/question", tags=["question"])

CurrentUser = Annotated[User, Depends(get_current_user)]


# 랜덤 자기성찰 질문 (인증 필요)
@router.get("/random", response_model=QuestionResponse)
async def get_random_question(current_user: CurrentUser):
    # 위치 인자로 전달(서비스는 _current_user로 받음)
    q = await svc_get_random_question(current_user)
    return QuestionResponse(id=q.id, content=q.question_text)
