from typing import Literal
from pydantic import BaseModel


class DailyTaskCreate(BaseModel):
    patient_id: str
    task_type: Literal[
        "game",
        "medicine",
        "doctor_appointment",
        "prescription",
        "meal",
        "hydration",
        "custom"
    ]
    task_description: str
    scheduled_time: str | None = None