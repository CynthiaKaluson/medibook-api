from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx
from app.core.config import settings
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


@router.get("/patient/google")
async def google_login():
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.GOOGLE_CLIENT_ID}"
        "&response_type=code"
        "&scope=openid email profile"
        "&redirect_uri=http://localhost:8000/api/v1/auth/patient/google/callback"
    )
    return {"url": google_auth_url}


@router.get("/patient/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": "http://localhost:8000/api/v1/auth/patient/google/callback",
                "grant_type": "authorization_code",
            },
        )
        token_data = token_response.json()

        if "error" in token_data:
            raise HTTPException(status_code=400, detail="Google OAuth failed")

        user_response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_info = user_response.json()

    google_id = user_info.get("id")
    email = user_info.get("email")
    full_name = user_info.get("name", email)

    result = await db.execute(select(Patient).where(Patient.email == email))
    patient = result.scalar_one_or_none()

    if not patient:
        patient = Patient(
            full_name=full_name,
            email=email,
            password_hash="",
            google_id=google_id,
        )
        db.add(patient)
        await db.commit()
        await db.refresh(patient)
    elif not patient.google_id:
        patient.google_id = google_id
        await db.commit()

    token = create_access_token({"sub": str(patient.id), "type": "patient"})
    return {"access_token": token, "token_type": "bearer", "patient": full_name}
