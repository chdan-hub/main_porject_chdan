from pydantic import BaseModel, EmailStr, Field


# 회원가입 요청 DTO
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# 로그인 요청 DTO (Swagger에서 body 로그인도 지원하고 싶을 때 사용)
class UserLogin(BaseModel):
    username_or_email: str
    password: str


# 토큰 응답 DTO
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# 유저 응답 DTO
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
