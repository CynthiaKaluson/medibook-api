from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_patient
from app.models.patient import Patient
from app.models.appointment import Appointment
from app.models.slot import Slot
from app.models.doctor import Doctor
from app.services.ai_service import suggest_best_slot, patient_chatbot
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter()


class SlotSuggestionRequest(BaseModel):
    doctor_id: uuid.UUID
    reason: str


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []


@router.post("/suggest-slot")
async def get_slot_suggestion(
    data: SlotSuggestionRequest,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient),
):
    # Get available slots for this doctor
    result = await db.execute(
        select(Slot).where(Slot.doctor_id == data.doctor_id, Slot.is_available == True)
    )
    slots = result.scalars().all()

    if not slots:
        raise HTTPException(
            status_code=404, detail="No available slots for this doctor"
        )

    # Get doctor specialization
    doctor_result = await db.execute(select(Doctor).where(Doctor.id == data.doctor_id))
    doctor = doctor_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    slots_data = [
        {
            "id": str(slot.id),
            "start_time": slot.start_time.strftime("%B %d, %Y at %I:%M %p"),
            "end_time": slot.end_time.strftime("%I:%M %p"),
        }
        for slot in slots
    ]

    suggestion = await suggest_best_slot(
        available_slots=slots_data,
        patient_reason=data.reason,
        doctor_specialization=doctor.specialization,
    )

    return {
        "suggestion": suggestion,
        "available_slots": slots_data,
        "doctor": doctor.full_name,
        "specialization": doctor.specialization,
    }


@router.post("/chat")
async def chat_with_medibot(
    data: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient),
):
    # Get patient's appointments
    result = await db.execute(
        select(Appointment).where(Appointment.patient_id == current_patient.id)
    )
    appointments = result.scalars().all()

    appointments_data = [
        {
            "id": str(a.id),
            "doctor_id": str(a.doctor_id),
            "status": a.status.value,
            "reason": a.reason,
            "created_at": a.created_at.strftime("%B %d, %Y"),
        }
        for a in appointments
    ]

    history = [{"role": m.role, "content": m.content} for m in data.history]

    response = await patient_chatbot(
        patient_name=current_patient.full_name,
        patient_email=current_patient.email,
        appointments=appointments_data,
        user_message=data.message,
        chat_history=history,
    )

    return {
        "response": response,
        "patient": current_patient.full_name,
    }
