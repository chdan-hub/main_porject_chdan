# app/models/question.py

from tortoise import fields
from tortoise.models import Model


class Question(Model):
    id = fields.IntField(pk=True)
    question_text = fields.TextField(null=False)

    def __str__(self):
        return self.question_text

    class Meta:
        table = "questions"
