from celery import Celery
from celery.schedules import crontab
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.slot import Slot
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.services.email_service import send_appointment_reminder
from app.core.config import settings

celery_app = Celery(
    "medibook",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.timezone = "UTC"

celery_app.conf.beat_schedule = {
    "send-reminders-every-hour": {
        "task": "app.tasks.reminder_tasks.send_24h_reminders",
        "schedule": crontab(minute=0, hour="*"),
    },
}


@celery_app.task(name="app.tasks.reminder_tasks.send_24h_reminders")
def send_24h_reminders():
    asyncio.run(_send_reminders())


async def _send_reminders():
    async with AsyncSessionLocal() as db:
        now = datetime.now(timezone.utc)
        window_start = now + timedelta(hours=23)
        window_end = now + timedelta(hours=25)

        result = await db.execute(
            select(Appointment, Slot, Patient, Doctor)
            .join(Slot, Slot.id == Appointment.slot_id)
            .join(Patient, Patient.id == Appointment.patient_id)
            .join(Doctor, Doctor.id == Appointment.doctor_id)
            .where(
                Appointment.status.in_(
                    [AppointmentStatus.pending, AppointmentStatus.confirmed]
                ),
                Slot.start_time >= window_start,
                Slot.start_time <= window_end,
            )
        )
        rows = result.all()

        for appointment, slot, patient, doctor in rows:
            await send_appointment_reminder(
                patient_email=patient.email,
                patient_name=patient.full_name,
                doctor_name=doctor.full_name,
                start_time=slot.start_time.strftime("%B %d, %Y at %I:%M %p"),
            )
