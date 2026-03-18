# 🏥 MediBook API

> **A production-ready Smart Appointment REST API for healthcare clinics — built with FastAPI, PostgreSQL, and AI.**

[![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.135-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://postgresql.org)
[![OpenAI](https://img.shields.io/badge/AI-GPT--4o--mini-purple?logo=openai)](https://openai.com)
[![Deployed on Render](https://img.shields.io/badge/Deployed-Render-46E3B7?logo=render)](https://medibook-api-9xi4.onrender.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌐 Live Demo

| Resource                          | Link                                          |
| --------------------------------- | --------------------------------------------- |
| 🚀 **Live API**                   | https://medibook-api-9xi4.onrender.com        |
| 📖 **Interactive Docs (Swagger)** | https://medibook-api-9xi4.onrender.com/docs   |
| ❤️ **Health Check**               | https://medibook-api-9xi4.onrender.com/health |

---

## 📌 What is MediBook?

MediBook is a backend API that powers a smart healthcare appointment booking system. It allows clinics to manage doctors and availability slots, while patients can book appointments, receive email confirmations, and interact with an AI assistant.

Built as a **portfolio project** to demonstrate real-world backend engineering skills — async Python, relational database design, JWT authentication, third-party integrations, AI features, and cloud deployment.

---

## ✨ Features

### 🔐 Authentication & Security

- Clinic and patient registration with **bcrypt password hashing**
- **JWT token-based authentication** with role separation (clinic vs patient)
- **Google OAuth 2.0** login for patients

### 🏥 Clinic Management

- Clinics register and manage their own doctors
- Full **multi-tenancy** — each clinic only sees their own data
- Doctor profiles with specialization, bio, and contact info

### 📅 Smart Appointment Booking

- Clinics create available time slots for doctors
- **Overlap detection** — no double-booking of slots
- **Conflict detection** — patients can't book two appointments at the same time
- Atomic slot locking — slot marked unavailable in the same DB transaction as booking
- Patients can cancel appointments (slot automatically freed)
- Clinics can update appointment status and add clinical notes

### 📧 Email Notifications

- **Confirmation email** on booking (human-readable date/time format)
- **Cancellation email** when appointment is cancelled
- **24-hour reminder emails** via Celery background tasks
- Powered by **Resend**

### 🤖 AI Features (OpenAI GPT-4o-mini)

- **Smart Slot Suggester** — recommends the best available slot based on patient's medical reason and urgency level
- **MediBot** — context-aware patient chatbot that knows the patient's appointment history and answers questions about the platform

### ⚙️ Background Tasks

- **Celery + Redis** task queue for automated appointment reminders
- Runs every hour, scans for appointments within the next 24 hours

---

## 🛠️ Tech Stack

```
| Layer | Technology | Why |
|---|---|---|
| Framework | FastAPI | Async, fast, auto-docs, modern Python |
| Database | PostgreSQL | Relational data integrity, industry standard |
| ORM | SQLAlchemy 2.0 (async) | Production-grade, type-safe queries |
| Migrations | Alembic | Version-controlled schema changes |
| Authentication | JWT + Google OAuth | Industry standard auth patterns |
| Email | Resend | Simple API, reliable delivery |
| AI | OpenAI GPT-4o-mini | Cost-efficient, powerful reasoning |
| Task Queue | Celery + Redis | Scalable background job processing |
| Deployment | Render | Cloud hosting with PostgreSQL |
| Validation | Pydantic v2 | Request/response validation |
```

---

## 📁 Project Structure

```
medibook-api/
├── app/
│   ├── main.py                  # FastAPI app entry point
│   ├── core/
│   │   ├── config.py            # Environment settings (Pydantic)
│   │   ├── security.py          # JWT + bcrypt
│   │   └── dependencies.py      # Auth dependencies
│   ├── db/
│   │   ├── base.py              # SQLAlchemy declarative base
│   │   └── session.py           # Async DB session
│   ├── models/                  # SQLAlchemy models
│   │   ├── clinic.py
│   │   ├── doctor.py
│   │   ├── patient.py
│   │   ├── slot.py
│   │   └── appointment.py
│   ├── schemas/                 # Pydantic schemas
│   ├── api/v1/endpoints/        # Route handlers
│   │   ├── auth.py
│   │   ├── doctors.py
│   │   ├── slots.py
│   │   ├── appointments.py
│   │   └── ai.py
│   ├── services/
│   │   ├── email_service.py     # Resend integration
│   │   └── ai_service.py        # OpenAI integration
│   └── tasks/
│       └── reminder_tasks.py    # Celery background tasks
├── alembic/                     # Database migrations
├── render.yaml                  # Render deployment config
├── requirements.txt
└── .env.example
```

---

## 🚀 Running Locally

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (for Celery)
- Conda or virtualenv

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/CynthiaKaluson/medibook-api.git
cd medibook-api

# 2. Create and activate environment
conda create -n medibook python=3.13
conda activate medibook

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 5. Run database migrations
alembic upgrade head

# 6. Start the server
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/docs` for the interactive API documentation.

---

## 🔑 Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/medibook_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=sk-...
RESEND_API_KEY=re_...
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
REDIS_URL=redis://localhost:6379/0
APP_ENV=development
```

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint                               | Description           | Auth |
| ------ | -------------------------------------- | --------------------- | ---- |
| POST   | `/api/v1/auth/clinic/register`         | Register a clinic     | None |
| POST   | `/api/v1/auth/clinic/login`            | Clinic login → JWT    | None |
| POST   | `/api/v1/auth/patient/register`        | Register a patient    | None |
| POST   | `/api/v1/auth/patient/login`           | Patient login → JWT   | None |
| GET    | `/api/v1/auth/patient/google`          | Google OAuth URL      | None |
| GET    | `/api/v1/auth/patient/google/callback` | Google OAuth callback | None |

### Doctors

| Method | Endpoint               | Description           | Auth       |
| ------ | ---------------------- | --------------------- | ---------- |
| POST   | `/api/v1/doctors/`     | Create doctor         | Clinic JWT |
| GET    | `/api/v1/doctors/`     | List clinic's doctors | Clinic JWT |
| GET    | `/api/v1/doctors/{id}` | Get doctor by ID      | Clinic JWT |
| DELETE | `/api/v1/doctors/{id}` | Delete doctor         | Clinic JWT |

### Slots

| Method | Endpoint                    | Description          | Auth       |
| ------ | --------------------------- | -------------------- | ---------- |
| POST   | `/api/v1/slots/`            | Create time slot     | Clinic JWT |
| GET    | `/api/v1/slots/doctor/{id}` | List available slots | None       |

### Appointments

| Method | Endpoint                           | Description             | Auth        |
| ------ | ---------------------------------- | ----------------------- | ----------- |
| POST   | `/api/v1/appointments/`            | Book appointment        | Patient JWT |
| GET    | `/api/v1/appointments/my`          | My appointments         | Patient JWT |
| PATCH  | `/api/v1/appointments/{id}/cancel` | Cancel appointment      | Patient JWT |
| PATCH  | `/api/v1/appointments/{id}/status` | Update status/notes     | Clinic JWT  |
| GET    | `/api/v1/appointments/clinic/all`  | All clinic appointments | Clinic JWT  |

### AI Features

| Method | Endpoint                  | Description            | Auth        |
| ------ | ------------------------- | ---------------------- | ----------- |
| POST   | `/api/v1/ai/suggest-slot` | AI slot recommendation | Patient JWT |
| POST   | `/api/v1/ai/chat`         | Chat with MediBot      | Patient JWT |

---

## 💡 Example Requests

### Book an Appointment

```bash
curl -X POST https://medibook-api-9xi4.onrender.com/api/v1/appointments/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slot_id": "uuid-here",
    "doctor_id": "uuid-here",
    "reason": "Annual checkup"
  }'
```

### AI Smart Slot Suggestion

```bash
curl -X POST https://medibook-api-9xi4.onrender.com/api/v1/ai/suggest-slot \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "doctor_id": "uuid-here",
    "reason": "Severe chest pain and difficulty breathing"
  }'
```

**Response:**

```json
{
  "suggestion": {
    "recommended_slot_id": "uuid-here",
    "reason": "Morning slot recommended for severe symptoms requiring prompt evaluation",
    "urgency": "high"
  },
  "doctor": "Dr. Chidi Okeke",
  "specialization": "Cardiologist"
}
```

### Chat with MediBot

```bash
curl -X POST https://medibook-api-9xi4.onrender.com/api/v1/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What appointments do I have coming up?",
    "history": []
  }'
```

**Response:**

```json
{
  "response": "You have one upcoming appointment — a routine checkup scheduled for March 20, 2026 at 09:00 AM with Dr. Chidi Okeke (Cardiologist). Would you like to make any changes?",
  "patient": "Ada Obi"
}
```

---

## 🏗️ Key Architecture Decisions

**Async everywhere** — FastAPI + SQLAlchemy 2.0 async + asyncpg means the API handles concurrent requests without blocking, which is critical for healthcare systems with simultaneous users.

**UUID primary keys** — All IDs are UUIDs instead of integers, preventing enumeration attacks where an attacker guesses resource IDs.

**Transactional slot locking** — When a patient books an appointment, the slot is marked unavailable in the same database commit as the appointment creation. This prevents race conditions where two patients book the same slot simultaneously.

**Multi-tenancy by design** — Every doctor and appointment query is scoped to the authenticated clinic's ID, ensuring clinics never see each other's data.

**Non-blocking email** — Email failures are caught and logged but never crash the booking flow. Patients get their appointment even if the email service is temporarily down.

---

## 👩🏽‍💻 Author

```

**Cynthia Kalu**
Junior Backend Developer
• [GitHub](https://github.com/CynthiaKaluson)
• [LinkedIn](https://www.linkedin.com/in/cynthia-kalu-okorie/)
```

---

## 📄 License

```

This project is licensed under the MIT License.
```
