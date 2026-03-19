import json
import time
import logging
from openai import OpenAI, APITimeoutError, RateLimitError, APIError
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)

MAX_RETRIES = 2
RETRY_DELAY = 5


def _call_openai_with_retry(kwargs: dict):
    """Call OpenAI with timeout and retry logic."""
    last_error = None

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                timeout=15,
                **kwargs,
            )
            return response
        except APITimeoutError as e:
            last_error = e
            logger.warning(f"OpenAI timeout on attempt {attempt + 1}/{MAX_RETRIES + 1}")
        except RateLimitError as e:
            last_error = e
            logger.warning(
                f"OpenAI rate limit on attempt {attempt + 1}/{MAX_RETRIES + 1}"
            )
        except APIError as e:
            last_error = e
            logger.warning(
                f"OpenAI API error on attempt {attempt + 1}/{MAX_RETRIES + 1}: {e}"
            )

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_DELAY)

    raise last_error


async def suggest_best_slot(
    available_slots: list,
    patient_reason: str,
    doctor_specialization: str,
) -> dict:
    slots_text = "\n".join(
        [
            f"- Slot ID: {s['id']}, Time: {s['start_time']} to {s['end_time']}"
            for s in available_slots
        ]
    )

    prompt = f"""
You are a smart medical appointment assistant for MediBook.
A patient needs an appointment with a {doctor_specialization} for: "{patient_reason}"
Available slots:
{slots_text}
Based on the reason and available times, suggest the BEST slot for this patient.
Consider that morning slots are generally better for serious medical concerns,
and afternoon slots for routine checkups.
Respond in this exact JSON format:
{{
    "recommended_slot_id": "the slot id here",
    "reason": "brief explanation why this slot is best",
    "urgency": "low | medium | high"
}}
"""

    response = _call_openai_with_retry(
        {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
        }
    )

    return json.loads(response.choices[0].message.content)


async def patient_chatbot(
    patient_name: str,
    patient_email: str,
    appointments: list,
    user_message: str,
    chat_history: list,
) -> str:
    appointments_text = (
        "\n".join(
            [
                f"- Appointment ID: {a['id']}, Doctor: {a['doctor_id']}, "
                f"Status: {a['status']}, Reason: {a['reason']}, Date: {a['created_at']}"
                for a in appointments
            ]
        )
        if appointments
        else "No appointments found."
    )

    system_prompt = f"""
You are MediBot, a friendly and professional AI assistant for MediBook — a smart healthcare appointment platform.
You are currently helping: {patient_name} ({patient_email})
Their appointment history:
{appointments_text}
Your responsibilities:
1. Answer questions about their appointments clearly
2. Explain how to book, cancel or reschedule appointments
3. Provide general guidance about the MediBook platform
4. Be empathetic and professional — this is a healthcare context
5. If asked about medical advice, always recommend they consult their doctor
Keep responses concise, warm, and helpful.
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in chat_history[-6:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    response = _call_openai_with_retry(
        {
            "model": "gpt-4o-mini",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500,
        }
    )

    return response.choices[0].message.content
