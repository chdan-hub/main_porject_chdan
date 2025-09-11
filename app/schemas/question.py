from pydantic import BaseModel, ConfigDict, Field


class QuestionResponse(BaseModel):
    id: int
    question_text: str = Field(examples=["오늘 나를 가장 웃게 만든 일은?"])
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"id": 3, "question_text": "오늘 나를 가장 웃게 만든 일은?"}]
        }
    )
