from tortoise import fields
from tortoise.models import Model

from app.models.quote import Quote
from app.models.user import User


class Bookmark(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User",
        related_name="bookmarks",  # 여기 수정
    )
    quote: fields.ForeignKeyRelation[Quote] = fields.ForeignKeyField(
        "models.Quote",
        related_name="bookmarks",  # 클래스 이름 사용
    )

    class Meta:
        table = "bookmarks"
        unique_together = ("user", "quote")  # 중복 북마크 방지
