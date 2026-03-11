import resend
import logging
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY
SENDER = "MediBook <onboarding@resend.dev>"
logger = logging.getLogger(__name__)


async def send_appointment_confirmation(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    specialization: str,
    start_time: str,
    end_time: str,
):
    try:
        resend.Emails.send(
            {
                "from": SENDER,
                "to": [patient_email],
                "subject": "✅ Appointment Confirmed — MediBook",
                "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #2c7be5;">MediBook — Appointment Confirmation</h2>
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your appointment has been successfully booked.</p>
                <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
                    <tr style="background: #f5f9ff;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Doctor</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{doctor_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Specialization</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{specialization}</td>
                    </tr>
                    <tr style="background: #f5f9ff;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Date & Time</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{start_time} — {end_time}</td>
                    </tr>
                </table>
                <p style="color: #666;">Please arrive 10 minutes early.</p>
                <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="color: #999; font-size: 12px;">This is an automated message from MediBook.</p>
            </div>
            """,
            }
        )
        logger.info(f"Confirmation email sent to {patient_email}")
    except Exception as e:
        logger.warning(f"Email failed (non-critical): {e}")


async def send_cancellation_email(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    start_time: str,
):
    try:
        resend.Emails.send(
            {
                "from": SENDER,
                "to": [patient_email],
                "subject": "❌ Appointment Cancelled — MediBook",
                "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #e53935;">MediBook — Appointment Cancelled</h2>
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>Your appointment with <strong>{doctor_name}</strong> scheduled for <strong>{start_time}</strong> has been cancelled.</p>
                <p style="color: #666;">You can book a new appointment anytime through MediBook.</p>
            </div>
            """,
            }
        )
        logger.info(f"Cancellation email sent to {patient_email}")
    except Exception as e:
        logger.warning(f"Email failed (non-critical): {e}")


async def send_appointment_reminder(
    patient_email: str,
    patient_name: str,
    doctor_name: str,
    start_time: str,
):
    try:
        resend.Emails.send(
            {
                "from": SENDER,
                "to": [patient_email],
                "subject": "⏰ Appointment Reminder — MediBook",
                "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
                <h2 style="color: #f0a500;">MediBook — Reminder</h2>
                <p>Dear <strong>{patient_name}</strong>,</p>
                <p>You have an appointment with <strong>{doctor_name}</strong> at <strong>{start_time}</strong>.</p>
                <p style="color: #666;">Please arrive 10 minutes early.</p>
            </div>
            """,
            }
        )
        logger.info(f"Reminder email sent to {patient_email}")
    except Exception as e:
        logger.warning(f"Email failed (non-critical): {e}")
