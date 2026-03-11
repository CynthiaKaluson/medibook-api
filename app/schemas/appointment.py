from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.models.appointment import AppointmentStatus


class AppointmentCreate(BaseModel):
    slot_id: UUID
    doctor_id: UUID
    reason: Optional[str] = None


class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    id: UUID
    patient_id: UUID
    doctor_id: UUID
    slot_id: UUID
    status: AppointmentStatus
    reason: Optional[str]
    notes: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
