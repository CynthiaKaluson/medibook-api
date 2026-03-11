from fastapi import APIRouter
from app.api.v1.endpoints import auth, doctors, slots

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
api_router.include_router(slots.router, prefix="/slots", tags=["Slots"])
