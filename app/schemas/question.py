from pydantic import BaseModel


class QuestionResponse(BaseModel):
    id: int
    content: str  # 모델의 question_text를 content로 매핑해 반환
