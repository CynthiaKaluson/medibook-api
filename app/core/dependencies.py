from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models.clinic import Clinic
from app.models.patient import Patient

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/clinic/login")


async def get_current_clinic(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Clinic:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    clinic_id: str = payload.get("sub")
    if clinic_id is None:
        raise credentials_exception
    result = await db.execute(select(Clinic).where(Clinic.id == clinic_id))
    clinic = result.scalar_one_or_none()
    if clinic is None:
        raise credentials_exception
    return clinic


async def get_current_patient(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> Patient:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    patient_id: str = payload.get("sub")
    if patient_id is None:
        raise credentials_exception
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if patient is None:
        raise credentials_exception
    return patient
