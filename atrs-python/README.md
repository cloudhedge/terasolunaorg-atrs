# ATRS Python - Airline Ticket Reservation System

Python/FastAPI migration of the ATRS Java application.

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env
# Edit .env with your database settings

# Run the application
uvicorn atrs.main:app --reload

# Open API docs
open http://localhost:8000/docs
```

## Project Structure

```
src/atrs/
├── main.py              # FastAPI application entry point
├── config/              # Configuration and database setup
├── models/              # Pydantic domain models
├── repositories/        # Data access layer (raw SQL)
├── services/            # Business logic layer
│   ├── auth/           # Authentication service
│   ├── ticket/         # Flight search and reservation
│   ├── member/         # Member management
│   └── report/         # Report generation
├── api/                 # REST API endpoints
│   └── v1/             # API version 1 routes
├── schemas/             # Request/Response Pydantic models
├── core/                # Utilities, exceptions, security
└── tasks/               # Background tasks (arq)
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/login` | POST | User authentication |
| `/api/v1/auth/logout` | POST | User logout |
| `/api/v1/flights/search` | GET | Search available flights |
| `/api/v1/reservations` | POST | Create reservation |
| `/api/v1/reservations/calculate-fare` | POST | Calculate fare |
| `/api/v1/members/register` | POST | Register new member |
| `/api/v1/members/me` | GET/PUT | Get/Update current member |

## Running Background Worker

```bash
# Start arq worker for async report generation
arq atrs.tasks.worker.WorkerSettings
```

## Requirements

- Python 3.11+
- PostgreSQL (same database as Java app)
- Redis (for background tasks)
