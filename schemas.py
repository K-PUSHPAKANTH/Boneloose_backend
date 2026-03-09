from pydantic import BaseModel

class RegisterSchema(BaseModel):
    full_name: str
    email: str
    phone: str
    password: str
    role: str = "dentist"

class LoginSchema(BaseModel):
    email: str
    password: str

class UpdateProfileSchema(BaseModel):
    full_name: str
    email: str
    role: str

from pydantic import BaseModel
from datetime import datetime

class AnalysisResponse(BaseModel):
    id: int
    patient_id: str
    prediction: str
    confidence: float
    created_at: datetime

class Config:
    from_attributes = True