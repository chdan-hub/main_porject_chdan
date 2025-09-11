from pydantic import BaseModel, ConfigDict, Field


class QuoteResponse(BaseModel):
    id: int
    content: str = Field(examples=["Stay hungry, stay foolish."])
    author: str | None = Field(default=None, examples=["Steve Jobs"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 42,
                    "content": "Stay hungry, stay foolish.",
                    "author": "Steve Jobs",
                }
            ]
        }
    )
