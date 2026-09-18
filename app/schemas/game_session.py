from pydantic import BaseModel, Field


class GameSessionCreate(BaseModel):
    patient_id: str
    game_id: int
    difficulty_level: int = Field(ge=1, le=5)