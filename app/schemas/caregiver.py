from pydantic import BaseModel


class CaregiverPatientCreate(BaseModel):
    caregiver_id: str
    patient_id: str