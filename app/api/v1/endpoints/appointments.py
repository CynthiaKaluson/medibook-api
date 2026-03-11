from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_patient, get_current_clinic
from app.models.appointment import Appointment, AppointmentStatus
from app.models.slot import Slot
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.clinic import Clinic
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
)
from app.services.email_service import (
    send_appointment_confirmation,
    send_cancellation_email,
)
from typing import List

router = APIRouter()


@router.post("/", response_model=AppointmentResponse, status_code=201)
async def book_appointment(
    data: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient),
):
    slot_result = await db.execute(
        select(Slot).where(Slot.id == data.slot_id, Slot.is_available == True)
    )
    slot = slot_result.scalar_one_or_none()
    if not slot:
        raise HTTPException(status_code=404, detail="Slot not found or already booked")

    doctor_result = await db.execute(
        select(Doctor).where(Doctor.id == data.doctor_id, Doctor.is_active == True)
    )
    doctor = doctor_result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    conflict = await db.execute(
        select(Appointment)
        .join(Slot)
        .where(
            Appointment.patient_id == current_patient.id,
            Appointment.status.in_(
                [AppointmentStatus.pending, AppointmentStatus.confirmed]
            ),
            Slot.start_time < slot.end_time,
            Slot.end_time > slot.start_time,
        )
    )
    if conflict.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="You already have an appointment at this time"
        )

    appointment = Appointment(
        patient_id=current_patient.id,
        doctor_id=data.doctor_id,
        slot_id=data.slot_id,
        reason=data.reason,
    )
    slot.is_available = False
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)

    await send_appointment_confirmation(
        patient_email=current_patient.email,
        patient_name=current_patient.full_name,
        doctor_name=doctor.full_name,
        specialization=doctor.specialization,
        start_time=slot.start_time.strftime("%B %d, %Y at %I:%M %p"),
        end_time=slot.end_time.strftime("%I:%M %p"),
    )

    return appointment


@router.get("/my", response_model=List[AppointmentResponse])
async def my_appointments(
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient),
):
    result = await db.execute(
        select(Appointment).where(Appointment.patient_id == current_patient.id)
    )
    return result.scalars().all()


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
async def cancel_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(get_db),
    current_patient: Patient = Depends(get_current_patient),
):
    result = await db.execute(
        select(Appointment).where(
            Appointment.id == appointment_id,
            Appointment.patient_id == current_patient.id,
        )
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if appointment.status == AppointmentStatus.cancelled:
        raise HTTPException(status_code=400, detail="Appointment already cancelled")

    appointment.status = AppointmentStatus.cancelled

    slot_result = await db.execute(select(Slot).where(Slot.id == appointment.slot_id))
    slot = slot_result.scalar_one_or_none()
    if slot:
        slot.is_available = True

    await db.commit()
    await db.refresh(appointment)

    await send_cancellation_email(
        patient_email=current_patient.email,
        patient_name=current_patient.full_name,
        doctor_name="Your Doctor",
        start_time=(
            slot.start_time.strftime("%B %d, %Y at %I:%M %p")
            if slot
            else "your scheduled time"
        ),
    )

    return appointment


@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
async def update_appointment_status(
    appointment_id: str,
    data: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(
        select(Appointment)
        .join(Doctor)
        .where(Appointment.id == appointment_id, Doctor.clinic_id == current_clinic.id)
    )
    appointment = result.scalar_one_or_none()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    if data.status:
        appointment.status = data.status
    if data.notes:
        appointment.notes = data.notes

    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.get("/clinic/all", response_model=List[AppointmentResponse])
async def clinic_appointments(
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(
        select(Appointment).join(Doctor).where(Doctor.clinic_id == current_clinic.id)
    )
    return result.scalars().all()
