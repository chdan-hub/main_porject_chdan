from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserResponse
from app.services.auth_service import (
    authenticate_and_issue_token,
    get_current_user,
    logout_current_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["auth"])


# 회원가입
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: UserCreate):
    user = await register_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )
    return UserResponse(id=user.id, username=user.username, email=user.email)


# 로그인 (OAuth2PasswordRequestForm: form-data 로 username / password)
# - username 자리에 "username 또는 email" 아무거나 넣어도 됩니다.
@router.post("/login", response_model=Token)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    access_token = await authenticate_and_issue_token(
        username_or_email=form.username,
        password=form.password,
    )
    return Token(access_token=access_token)


# (선택) 바디 로그인도 지원하고 싶다면
@router.post("/login-body", response_model=Token, include_in_schema=False)
async def login_body(payload: UserLogin):
    access_token = await authenticate_and_issue_token(
        username_or_email=payload.username_or_email,
        password=payload.password,
    )
    return Token(access_token=access_token)


# 내 정보 조회 (보호됨)
@router.get("/me", response_model=UserResponse)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return UserResponse(
        id=current_user.id, username=current_user.username, email=current_user.email
    )


# (선택) 로그아웃: 현재 토큰을 블랙리스트에 등록 (Authorization 헤더 필요)
@router.post("/logout", status_code=204)
async def logout(_: Annotated[None, Depends(logout_current_token)]):
    return
