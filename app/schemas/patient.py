from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime, date
from typing import Optional


class PatientRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None


class PatientLogin(BaseModel):
    email: EmailStr
    password: str


class PatientResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone: Optional[str]
    date_of_birth: Optional[date]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
