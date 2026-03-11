from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class SlotCreate(BaseModel):
    doctor_id: UUID
    start_time: datetime
    end_time: datetime


class SlotResponse(BaseModel):
    id: UUID
    doctor_id: UUID
    start_time: datetime
    end_time: datetime
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}
