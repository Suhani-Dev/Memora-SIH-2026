from pydantic import BaseModel, Field


class GameResultCreate(BaseModel):
    session_id: str
    score: int
    accuracy: float = Field(ge=0, le=100)
    correct_answers: int
    total_questions: int
    mistakes: int
    response_time_avg: float
    completion_time: float