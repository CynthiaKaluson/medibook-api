from fastapi import APIRouter
from app.api.v1.endpoints import auth, doctors, slots, appointments, ai

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
api_router.include_router(slots.router, prefix="/slots", tags=["Slots"])
api_router.include_router(
    appointments.router, prefix="/appointments", tags=["Appointments"]
)
api_router.include_router(ai.router, prefix="/ai", tags=["AI Features"])
