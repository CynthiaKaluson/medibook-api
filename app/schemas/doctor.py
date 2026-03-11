from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class DoctorCreate(BaseModel):
    full_name: str
    email: EmailStr
    specialization: str
    phone: Optional[str] = None
    bio: Optional[str] = None


class DoctorResponse(BaseModel):
    id: UUID
    clinic_id: UUID
    full_name: str
    email: EmailStr
    specialization: str
    phone: Optional[str]
    bio: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
