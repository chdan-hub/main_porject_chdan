# app/models/quote.py

from tortoise import fields
from tortoise.models import Model


class Quote(Model):
    id = fields.IntField(pk=True)
    content = fields.TextField(null=False)
    author = fields.CharField(max_length=100)

    def __str__(self):
        return self.author

    class Meta:
        table = "quotes"
