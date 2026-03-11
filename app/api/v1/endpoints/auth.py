from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.models.clinic import Clinic
from app.models.patient import Patient
from app.schemas.clinic import (
    ClinicRegister,
    ClinicLogin,
    ClinicResponse,
    TokenResponse,
)
from app.schemas.patient import PatientRegister, PatientLogin, PatientResponse

router = APIRouter()


@router.post("/clinic/register", response_model=ClinicResponse, status_code=201)
async def register_clinic(data: ClinicRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Clinic).where(Clinic.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    clinic = Clinic(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        phone=data.phone,
        address=data.address,
    )
    db.add(clinic)
    await db.commit()
    await db.refresh(clinic)
    return clinic


@router.post("/clinic/login", response_model=TokenResponse)
async def login_clinic(data: ClinicLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Clinic).where(Clinic.email == data.email))
    clinic = result.scalar_one_or_none()
    if not clinic or not verify_password(data.password, clinic.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(clinic.id), "type": "clinic"})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/patient/register", response_model=PatientResponse, status_code=201)
async def register_patient(data: PatientRegister, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    patient = Patient(
        full_name=data.full_name,
        email=data.email,
        password_hash=hash_password(data.password),
        phone=data.phone,
        date_of_birth=data.date_of_birth,
    )
    db.add(patient)
    await db.commit()
    await db.refresh(patient)
    return patient


@router.post("/patient/login", response_model=TokenResponse)
async def login_patient(data: PatientLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Patient).where(Patient.email == data.email))
    patient = result.scalar_one_or_none()
    if not patient or not verify_password(data.password, patient.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(patient.id), "type": "patient"})
    return {"access_token": token, "token_type": "bearer"}
