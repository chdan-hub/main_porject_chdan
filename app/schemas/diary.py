from datetime import datetime

from pydantic import BaseModel, Field


class DiaryCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(min_length=1)


class DiaryUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, min_length=1)


class DiaryResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime
    updated_at: datetime
