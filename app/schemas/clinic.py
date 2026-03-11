from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class ClinicRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None


class ClinicLogin(BaseModel):
    email: EmailStr
    password: str


class ClinicResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    address: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
