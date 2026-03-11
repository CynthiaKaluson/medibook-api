from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.dependencies import get_current_clinic
from app.models.doctor import Doctor
from app.models.clinic import Clinic
from app.schemas.doctor import DoctorCreate, DoctorResponse
from typing import List

router = APIRouter()


@router.post("/", response_model=DoctorResponse, status_code=201)
async def create_doctor(
    data: DoctorCreate,
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(select(Doctor).where(Doctor.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Doctor email already exists")
    doctor = Doctor(
        clinic_id=current_clinic.id,
        full_name=data.full_name,
        email=data.email,
        specialization=data.specialization,
        phone=data.phone,
        bio=data.bio,
    )
    db.add(doctor)
    await db.commit()
    await db.refresh(doctor)
    return doctor


@router.get("/", response_model=List[DoctorResponse])
async def list_doctors(
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(
        select(Doctor).where(Doctor.clinic_id == current_clinic.id)
    )
    return result.scalars().all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(
    doctor_id: str,
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id, Doctor.clinic_id == current_clinic.id
        )
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.delete("/{doctor_id}", status_code=204)
async def delete_doctor(
    doctor_id: str,
    db: AsyncSession = Depends(get_db),
    current_clinic: Clinic = Depends(get_current_clinic),
):
    result = await db.execute(
        select(Doctor).where(
            Doctor.id == doctor_id, Doctor.clinic_id == current_clinic.id
        )
    )
    doctor = result.scalar_one_or_none()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    await db.delete(doctor)
    await db.commit()
