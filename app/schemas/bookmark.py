from pydantic import BaseModel, ConfigDict

from app.schemas.quote import QuoteResponse


class BookmarkResponse(BaseModel):
    id: int
    quote: QuoteResponse
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": 7,
                    "quote": {
                        "id": 42,
                        "content": "Stay hungry, stay foolish.",
                        "author": "Steve Jobs",
                    },
                }
            ]
        }
    )
