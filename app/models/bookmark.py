# app/models/bookmark.py

from tortoise import fields
from tortoise.models import Model

from app.models.quote import Quote
from app.models.user import User


class Bookmark(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "app.models.User", related_name="user_questions"
    )
    quote: fields.ForeignKeyRelation[Quote] = fields.ForeignKeyField(
        "app.models.quote", related_name="user_questions"
    )

    class Meta:
        table = "bookmarks"
        unique_together = ("user", "quote")  # 중복 북마크 방지
