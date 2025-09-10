import random
from typing import Iterable, Optional

from app.models.quote import Quote


async def get_random_quote() -> Optional[Quote]:
    count = await Quote.all().count()
    if count == 0:
        return None
    offset = random.randint(0, count - 1)
    return await Quote.all().offset(offset).limit(1).first()


async def get_quote_by_id(quote_id: int) -> Optional[Quote]:
    return await Quote.get_or_none(id=quote_id)


async def list_quotes(limit: int = 20, offset: int = 0) -> Iterable[Quote]:
    return await Quote.all().order_by("-id").offset(offset).limit(limit)
