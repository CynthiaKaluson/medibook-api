from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_clinic
from app.models.slot import Slot
from app.models.doctor import Doctor
from app.models.clinic import Clinic
from app.schemas.slot import SlotCreate, SlotResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=SlotResponse, status_code=201)
async def create_slot(
    data: SlotCreate,
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == data.doctor_id, Doctor.clinic_id == current_clinic.id
        )
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found in your clinic")

    if data.start_time >= data.end_time:
        raise HTTPException(
            status_code=400, detail="start_time must be before end_time"
        )

    overlap = await db.execute(
        select(Slot).where(
            Slot.doctor_id == data.doctor_id,
            Slot.start_time < data.end_time,
            Slot.end_time > data.start_time,
        )
    )
    if overlap.scalar_one_or_none():
        raise HTTPException(
            status_code=409, detail="Slot overlaps with an existing slot"
        )

    slot = Slot(
        doctor_id=data.doctor_id,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(slot)
    await db.commit()
    await db.refresh(slot)
    return slot


@router.get("/doctor/{doctor_id}", response_model=List[SlotResponse])
async def get_doctor_slots(doctor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Slot).where(Slot.doctor_id == doctor_id, Slot.is_available == True)
    )
    return result.scalars().all()
