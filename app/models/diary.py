from tortoise import fields
from tortoise.models import Model

from app.models.user import User


class Diary(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255, null=False)
    content = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="diaries"
    )

    def __str__(self):
        return self.title

    class Meta:
        table = "diaries"
