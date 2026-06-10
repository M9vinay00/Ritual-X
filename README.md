# Ritual-X

Ritual-x is an asynchronous FastAPI backend for discovering pandits, managing service availability, creating bookings, handling payments, and collecting ratings.

## What It Does

- User registration, login, password reset, and profile lookup
- Pandit profile management, service listings, and availability slots
- Booking lifecycle actions such as create, approve, reject, complete, and cancel
- Payment recording and payment history
- Ratings for pandits and rating history for users
- Admin oversight for pandit approvals, user browsing, revenue, and reporting

## Tech Stack

- FastAPI
- SQLAlchemy 2.x with async sessions
- PostgreSQL via `asyncpg`
- Alembic migrations
- JWT authentication
- SMTP email support for password resets

## Prerequisites

- Python 3.10+ recommended
- PostgreSQL database
- `pip` for dependency installation

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the required settings.

## Environment Variables

Minimum required:

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/pandit_hub
JWT_SECRET_KEY=change-me-in-production
```

Optional but commonly used:

```env
PROJECT_NAME=Ritual-X
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_BASE_URL=http://127.0.0.1:8000
FORGOT_PASSWORD_EXPIRE_MINUTES=15

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
SMTP_FROM_EMAIL=noreply@example.com
SMTP_USE_TLS=true

ADMIN_SEED_ON_STARTUP=false
ADMIN_NAME=Super Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your-admin-password
ADMIN_PHONE=9999999999
```

## Database

Run migrations with Alembic:

```bash
alembic upgrade head
```

The application also seeds reference data on startup:

- Roles
- States and cities
- Languages
- Services

If `ADMIN_SEED_ON_STARTUP=true` and admin credentials are provided, it also creates a super admin account.

You can also run the seed helper directly:

```bash
python -m app.utils.seed
```

## Run The API

Start the development server with Uvicorn:

```bash
uvicorn app.main:app --reload
```

By default the app is available at:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## API Overview

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/forgot-password`
- `POST /auth/reset-password`
- `GET /auth/me`

### Pandits

- `GET /pandits/search`
- `GET /pandits/profile`
- `PUT /pandits/profile`
- `POST /pandits/slots`
- `GET /pandits/slots`
- `POST /pandits/services`
- `DELETE /pandits/services/{service_name}`
- `GET /pandits/{pandit_id}`
- `GET /pandits/{pandit_id}/slots`
- `PUT /pandits/slots/{slot_id}`
- `DELETE /pandits/slots/{slot_id}`

### Bookings

- `POST /bookings`
- `GET /bookings/user`
- `GET /bookings/pandit`
- `GET /bookings/{booking_id}`
- `PATCH /bookings/{booking_id}/approve`
- `PATCH /bookings/{booking_id}/reject`
- `PATCH /bookings/{booking_id}/complete`
- `DELETE /bookings/{booking_id}`

### Payments

- `POST /payments`
- `GET /payments/user`

### Ratings

- `POST /ratings`
- `GET /ratings/me`
- `GET /pandits/{pandit_id}/ratings`

### Admin

- `GET /admin/pandits`
- `PATCH /admin/pandits/{pandit_id}/approve`
- `PATCH /admin/pandits/{pandit_id}/reject`
- `PATCH /admin/pandits/{pandit_id}/deactivate`
- `PATCH /admin/pandits/{pandit_id}/activate`
- `GET /admin/users`
- `GET /admin/revenue`
- `GET /admin/pandits/top-rated`
- `GET /admin/services/popular`

## Project Structure

- `app/main.py` application entry point and global exception handlers
- `app/core/` settings and security helpers
- `app/database.py` async engine and session factory
- `app/models/` SQLAlchemy models and enums
- `app/schemas/` Pydantic request and response schemas
- `app/services/` business logic layer
- `app/repositories/` database access layer
- `app/routers/` API route definitions
- `app/utils/` seed and email helpers
- `alembic/` database migration files

## Notes

- The API returns a shared response envelope for most endpoints.
- Password reset links are built from `APP_BASE_URL`.
- Database and auth settings are loaded from environment variables using `python-dotenv`.

