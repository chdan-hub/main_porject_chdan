from tortoise import fields
from tortoise.models import Model

from app.models.user import User


class TokenBlacklist(Model):
    """
    로그아웃된 JWT 토큰을 저장하여 보안을 강화합니다.
    """

    id = fields.IntField(pk=True)
    token = fields.CharField(max_length=500, unique=True, null=False)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "app.models.User", related_name="token_blacklist"
    )
    expired_at = fields.DatetimeField(null=False)

    class Meta:
        table = "token_blacklist"
