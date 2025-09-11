from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DiaryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255, examples=["오늘의 회고"])
    content: str = Field(
        min_length=1, examples=["오늘은 이런 걸 배웠고, 이렇게 느꼈다."]
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "오늘의 회고", "content": "테스트를 정리하고 배운 점을 기록"}
            ]
        }
    )


class DiaryUpdate(BaseModel):
    title: str | None = Field(
        default=None, min_length=1, max_length=255, examples=["제목 수정"]
    )
    content: str | None = Field(default=None, min_length=1, examples=["내용 수정"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "오늘의 회고(수정)",
                    "content": "리팩터링 방향을 정리하고 내일 계획 수립",
                }
            ]
        }
    )


class DiaryResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 10,
                    "title": "오늘의 회고",
                    "content": "정리...",
                    "user_id": 1,
                    "created_at": "2025-09-10T12:34:56Z",
                    "updated_at": "2025-09-10T12:35:10Z",
                }
            ]
        }
    )
