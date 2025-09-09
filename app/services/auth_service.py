from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, status

from app.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    oauth2_scheme,
    verify_password,
)
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User
from app.repositories.user_repo import (
    create_user,
    get_by_email,
    get_by_id,
    get_by_username,
)

# ---------- 유저 조회 유틸 ----------


async def _find_user_by_username_or_email(username_or_email: str) -> Optional[User]:
    user = await get_by_username(username_or_email)
    if user:
        return user
    return await get_by_email(username_or_email)


# ---------- 회원가입 ----------


async def register_user(username: str, email: str, password: str) -> User:
    # 중복 체크
    if await get_by_username(username):
        raise HTTPException(status_code=400, detail="이미 사용 중인 사용자명입니다.")
    if await get_by_email(email):
        raise HTTPException(status_code=400, detail="이미 가입된 이메일입니다.")

    pw_hash = get_password_hash(password)
    user = await create_user(username=username, email=email, password_hash=pw_hash)
    return user


# ---------- 로그인 (토큰 발급) ----------


async def authenticate_and_issue_token(username_or_email: str, password: str) -> str:
    user = await _find_user_by_username_or_email(username_or_email)
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디(또는 이메일) 혹은 비밀번호가 올바르지 않습니다.",
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")
    # JWT 생성 (sub에 user.id 저장)
    token = create_access_token({"sub": str(user.id)})
    return token


# ---------- 현재 로그인 사용자 의존성 ----------


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    """
    - Authorization: Bearer <token> 에서 토큰 추출
    - JWT 디코드 / 블랙리스트 확인 / 유저 조회 / 활성화 확인
    """
    # 1) 토큰 블랙리스트 체크(로그아웃 처리된 토큰)
    if await TokenBlacklist.filter(token=token).exists():
        raise HTTPException(
            status_code=401, detail="만료되었거나 로그아웃된 토큰입니다."
        )

    # 2) JWT 디코드
    payload = decode_token(token, refresh=False)
    if not payload:
        raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=401, detail="토큰에 사용자 정보가 없습니다.")

    # 3) 만료(exp) 검증 (decode_token이 만료 시 None을 리턴하도록 구현돼 있어도 안전망)
    exp = payload.get("exp")
    if exp is not None:
        now_ts = int(datetime.now(timezone.utc).timestamp())
        if now_ts >= int(exp):
            raise HTTPException(status_code=401, detail="토큰이 만료되었습니다.")

    # 4) 사용자 조회
    user = await get_by_id(int(sub))
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="비활성화된 계정입니다.")

    return user


# ---------- (선택) 로그아웃 ----------


async def logout_current_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """
    현재 토큰을 블랙리스트에 저장하여 재사용을 차단합니다.
    """
    payload = decode_token(token, refresh=False)
    if not payload:
        # 이미 유효하지 않으면 그냥 통과
        return

    exp = payload.get("exp")
    expired_at = (
        datetime.fromtimestamp(exp, tz=timezone.utc)
        if exp
        else datetime.now(timezone.utc)
    )

    # 중복 저장 방지
    if await TokenBlacklist.filter(token=token).exists():
        return

    await TokenBlacklist.create(
        token=token,
        user=current_user,
        expired_at=expired_at,
    )
