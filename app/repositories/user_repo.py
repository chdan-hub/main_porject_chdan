from typing import Optional

from app.models.user import User


# 이메일로 조회
async def get_by_email(email: str) -> Optional[User]:
    return await User.get_or_none(email=email)


# 사용자명으로 조회
async def get_by_username(username: str) -> Optional[User]:
    return await User.get_or_none(username=username)


# PK(id)로 조회
async def get_by_id(user_id: int) -> Optional[User]:
    return await User.get_or_none(id=user_id)


# 생성
async def create_user(*, username: str, email: str, password_hash: str) -> User:
    return await User.create(
        username=username,
        email=email,
        password_hash=password_hash,
        is_active=True,
    )
