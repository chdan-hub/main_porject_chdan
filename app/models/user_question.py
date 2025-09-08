# app/models/user_question.py

from tortoise import fields
from tortoise.models import Model

from app.models.question import Question
from app.models.user import User


class UserQuestion(Model):
    id = fields.IntField(pk=True)
    user: fields.ForeignKeyRelation[User] = fields.ForeignKeyField(
        "app.models.User", related_name="user_questions"
    )
    question: fields.ForeignKeyRelation[Question] = fields.ForeignKeyField(
        "app.models.Question", related_name="user_questions"
    )

    class Meta:
        table = "user_questions"
        unique_together = ("user", "question")
