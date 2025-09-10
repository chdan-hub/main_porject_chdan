# app/models/user.py

from tortoise import fields
from tortoise.models import Model


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50, unique=True, null=False)
    email = fields.CharField(max_length=100, unique=True, null=False)
    password_hash = fields.CharField(max_length=255, null=False)
    is_active = fields.BooleanField(default=True)  # <-- 이 줄을 추가하세요.
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        table = "users"
