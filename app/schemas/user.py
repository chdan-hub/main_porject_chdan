from pydantic import BaseModel, ConfigDict, EmailStr, Field


# 회원가입 요청 DTO
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, examples=["jane"])
    email: EmailStr = Field(examples=["jane@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["secret123!"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "username": "jane",
                    "email": "jane@example.com",
                    "password": "secret123!",
                }
            ]
        }
    )


# 로그인 요청 DTO (Swagger에서 body 로그인도 지원하고 싶을 때 사용)
class UserLogin(BaseModel):
    username_or_email: str = Field(examples=["jane", "jane@example.com"])
    password: str = Field(min_length=8, max_length=128, examples=["secret123!"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"username_or_email": "jane", "password": "secret123!"}]
        }
    )


# 토큰 응답 DTO
class Token(BaseModel):
    access_token: str = Field(examples=["<JWT_ACCESS_TOKEN>"])
    token_type: str = Field(default="bearer", examples=["bearer"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                }
            ]
        }
    )


# 유저 응답 DTO
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"id": 1, "username": "jane", "email": "jane@example.com"}]
        }
    )
