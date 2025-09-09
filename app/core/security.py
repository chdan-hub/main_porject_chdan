# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# ===== Exported constants (auth.py 등에서 import해서 사용 가능) =====
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
# refresh token은 별도의 secret을 쓰는 것이 권장됨(없으면 ACCESS와 동일 키 사용)
REFRESH_SECRET_KEY: str = getattr(settings, "REFRESH_SECRET_KEY", SECRET_KEY)

ACCESS_TOKEN_EXPIRE_MINUTES: int = getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 60)
REFRESH_TOKEN_EXPIRE_DAYS: int = getattr(settings, "REFRESH_TOKEN_EXPIRE_DAYS", 7)

# OAuth2 password flow - tokenUrl은 실제 라우터 경로(/auth/login)로 맞춤
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===== Password helpers =====
def get_password_hash(password: str) -> str:
    """평문 비밀번호를 해싱합니다."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시를 비교해 일치 여부를 반환합니다."""
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT helpers =====
def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Access Token 생성.
    data 예: {"sub": "<user_id>"}
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode = {**data, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Refresh Token 생성.
    기본 만료: REFRESH_TOKEN_EXPIRE_DAYS (기본 7일)
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    to_encode = {**data, "exp": expire}
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str, refresh: bool = False) -> Optional[Dict[str, Any]]:
    """
    JWT 디코드 유틸.
    refresh=True 면 REFRESH_SECRET_KEY로 검증.
    유효하지 않으면 None 반환.
    """
    try:
        key = REFRESH_SECRET_KEY if refresh else SECRET_KEY
        payload = jwt.decode(token, key, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
