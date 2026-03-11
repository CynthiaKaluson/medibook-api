from celery import Celery
from app.core.config import settings
import resend

celery_app = Celery(
    "medibook",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Lagos",
    enable_utc=True,
)

resend.api_key = settings.RESEND_API_KEY
SENDER = "MediBook <onboarding@resend.dev>"


@celery_app.task(name="send_reminder_email")
def send_reminder_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    start_time: str,
):
    params = {
        "from": SENDER,
        "to": [patient_email],
        "subject": "⏰ Appointment Reminder — MediBook",
        "html": f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #f0a500;">MediBook — Appointment Reminder</h2>
            <p>Dear <strong>{patient_name}</strong>,</p>
            <p>This is a reminder about your upcoming appointment with <strong>{doctor_name}</strong> at <strong>{start_time}</strong>.</p>
            <p style="color: #666;">Please arrive 10 minutes early.</p>
        </div>
        """,
    }
    resend.Emails.send(params)
