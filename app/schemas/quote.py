from pydantic import BaseModel


class QuoteResponse(BaseModel):
    id: int
    content: str
    author: str | None = None
