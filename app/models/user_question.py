from tortoise import fields
from tortoise.models import Model

from app.models.question import Question
from app.models.user import User


class UserQuestion(Model):
    id = fields.IntField(pk=True)

    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "models.User", related_name="user_questions", on_delete=fields.RESTRICT
    )
    question: fields.ForeignKeyRelation[Question] = fields.ForeignKeyField(
        "models.Question", related_name="user_questions", on_delete=fields.RESTRICT
    )

    # 사용자가 해당 질문을 본/답한 기록
    seen = fields.BooleanField(default=True)
    seen_at = fields.DatetimeField(auto_now_add=True)

    answered = fields.BooleanField(default=False)
    answered_at = fields.DatetimeField(null=True)

    class Meta:
        table = "user_questions"
        unique_together = (("user", "question"),)
