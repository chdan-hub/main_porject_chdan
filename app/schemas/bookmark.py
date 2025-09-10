from pydantic import BaseModel

from app.schemas.quote import QuoteResponse


class BookmarkResponse(BaseModel):
    id: int
    quote: QuoteResponse
