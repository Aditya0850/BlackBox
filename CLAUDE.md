# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Python/FastAPI)
- **Run the backend**: `docker compose up backend` or `docker compose up` (starts all services)
- **Run migrations**: `docker compose exec backend alembic upgrade head`
- **Create migration**: `docker compose exec backend alembic revision -m "description"`
- **Run tests**: `docker compose exec backend pytest`
- **Run specific test**: `docker compose exec backend pytest path/to/test.py::test_function`
- **Run unit tests**: `docker compose exec backend pytest backend/tests/unit/`
- **Run integration tests**: `docker compose exec backend pytest backend/tests/integration/`
- **Run contract tests**: `docker compose exec backend pytest backend/tests/contract/`
- **Start backend in dev mode**: `docker compose up backend` (auto-reloads on code changes via volume mount)

### Frontend (React/Vite/TypeScript)
- **Run frontend**: `docker compose up frontend` or `docker compose up` (starts all services)
- **Frontend dev server**: Available at http://localhost:3000 with HMR
- **Install frontend dependencies**: `docker compose run --rm frontend npm ci`
- **Build frontend**: `docker compose run --rm frontend npm run build`
- **Preview build**: `docker compose run --rm frontend npm run preview`

### General
- **Start all services**: `docker compose up`
- **Start all services in background**: `docker compose up -d`
- **Stop all services**: `docker compose down`
- **View logs**: `docker compose logs -f [service_name]`
- **Rebuild and restart**: `docker compose up --build`

## Code Architecture & Structure

### Backend - Clean Architecture
The backend follows Clean Architecture with these layers:
- **api/**: HTTP layer only (FastAPI routers, dependency injection)
- **application/**: Use cases (business logic orchestration)
- **domain/**: Pure domain models (entities, events, value objects) - no framework dependencies
- **infrastructure/**: External service implementations (DB, MinIO, Redis, plugins)
- **pipeline/**: Evidence processing orchestrator and stage contracts
- **config.py**: Pydantic-based settings management

### Domain-Driven Design
- **PostgreSQL Schemas**:
  - `intel.*`: Machine knowledge (OCR results, AI summaries, etc.)
  - `audit.*`: Append-only audit log (no UPDATE/DELETE grants)
  - `notebook.*`: Reserved for future human-authored content (Investigation Notebook)

### Key Infrastructure Components
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0 ORM
- **Migrations**: Alembic for schema version control
- **Storage**: MinIO (S3-compatible) for raw evidence storage
- **Queue**: Redis 7 for future pipeline workers
- **API**: FastAPI with automatic OpenAPI/Swagger docs at /docs

### Frontend
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development server
- **State Management**: To be implemented in later slices
- **Styling**: Plain CSS/Tailwind (to be added)

### Containerization & DevOps
- **Orchestration**: Docker Compose defines all services
- **Health Checks**: Built-in for PostgreSQL, MinIO, Redis
- **Volume Mounts**: Enable hot reloading for backend and frontend during development
- **Environment**: `.env` file for configuration (matches docker-compose service names)

### API Conventions
- **Versioning endpoints under `/api/v1`
- Mutating endpoints require `reason` field for audit logging
- Error responses follow `{ error: { code, message, details } }` format
- Cursor-based pagination for list endpoints

## Verification Endpoints
- **Health Check**: `GET /health` - verifies PostgreSQL, Redis, MinIO
- **API Docs**: `GET /docs` - Swagger UI
- **Alternative Docs**: `GET /redoc` - ReDoc documentation