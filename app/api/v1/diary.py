from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from app.models.user import User
from app.schemas.diary import DiaryCreate, DiaryResponse, DiaryUpdate
from app.services.auth_service import get_current_user
from app.services.diary_service import (
    svc_create_diary,
    svc_delete_my_diary,
    svc_get_my_diary,
    svc_list_my_diaries,
    svc_update_my_diary,
)

router = APIRouter(prefix="/diary", tags=["diary"])

CurrentUser = Annotated[User, Depends(get_current_user)]  # 인증 필수 (B008 회피)


def to_response(d) -> DiaryResponse:
    return DiaryResponse(
        id=d.id,
        title=d.title,
        content=d.content,
        user_id=d.user_id,  # FK의 원시 키
        created_at=d.created_at,
        updated_at=d.updated_at,
    )


@router.post("", response_model=DiaryResponse, status_code=status.HTTP_201_CREATED)
async def create_diary(payload: DiaryCreate, current_user: CurrentUser):
    diary = await svc_create_diary(
        current_user=current_user,
        title=payload.title,
        content=payload.content,
    )
    return to_response(diary)


@router.get("", response_model=list[DiaryResponse])
async def list_my_diaries(
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    diaries = await svc_list_my_diaries(
        current_user=current_user, limit=limit, offset=offset
    )
    return [to_response(d) for d in diaries]


@router.get("/{diary_id}", response_model=DiaryResponse)
async def get_my_diary(diary_id: int, current_user: CurrentUser):
    diary = await svc_get_my_diary(current_user=current_user, diary_id=diary_id)
    return to_response(diary)


@router.put("/{diary_id}", response_model=DiaryResponse)
async def update_my_diary(
    diary_id: int, payload: DiaryUpdate, current_user: CurrentUser
):
    diary = await svc_update_my_diary(
        current_user=current_user,
        diary_id=diary_id,
        title=payload.title,
        content=payload.content,
    )
    return to_response(diary)


@router.delete("/{diary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_diary(diary_id: int, current_user: CurrentUser):
    await svc_delete_my_diary(current_user=current_user, diary_id=diary_id)
    return
