from tortoise import fields
from tortoise.models import Model

from app.models.user import User


class TokenBlacklist(Model):
    """
    로그아웃된 JWT 토큰을 저장하여 보안을 강화합니다.
    """

    id = fields.IntField(primary_key=True)
    token = fields.CharField(max_length=500, unique=True, null=False)
    # 아래 라인의 "models.User"를 "app.models.User"로 변경합니다.
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="token_blacklist"
    )
    expired_at = fields.DatetimeField(null=False)

    class Meta:
        table = "token_blacklist"
