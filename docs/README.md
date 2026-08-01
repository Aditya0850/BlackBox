# BlackBox

## Project Overview
BlackBox is a digital forensic evidence management platform designed to help investigators securely manage cases, evidence, metadata, and chain of custody records. This repository contains the foundation (Slice 1) of the platform, which sets up the core infrastructure upon which future features will be built.

## Features (Slice 1 — Project Foundation)
- **Backend**: FastAPI application with clean architecture boundaries (api, application, domain, infrastructure, pipeline)
- **Database**: PostgreSQL with `intel` and `audit` schemas created via Alembic migration
- **Object Storage**: MinIO bucket for raw evidence storage (bucket created on startup if missing)
- **Queue**: Redis connection configured (for future pipeline workers)
- **Frontend**: React + TypeScript + Vite development server (minimal shell)
- **Containerization**: Docker Compose orchestrates all services
- **Health Check**: Real-time verification endpoint (`GET /health`) that checks PostgreSQL, Redis, and MinIO availability
- **Configuration**: Type-safe settings management via Pydantic (`backend/src/config.py`)
- **Database Migrations**: Alembic configured for version-controlled schema evolution

## Tech Stack
- **Backend**: 
  - Language: Python 3.12
  - Framework: FastAPI
  - ORM: SQLAlchemy 2.0
  - Migration: Alembic
  - Dependency Injection: Pydantic Settings
- **Database**: 
  - PostgreSQL 15 (with `intel` and `audit` schemas)
- **Storage**: 
  - MinIO (S3-compatible object storage)
- **Queue**: 
  - Redis 7
- **Frontend**:
  - Language: TypeScript
  - Framework: React 18
  - Build Tool: Vite
- **DevOps**:
  - Containerization: Docker, Docker Compose
  - CI/CD: Ready for GitHub Actions (to be added)

## Folder Structure
```
blackbox/
├── backend/                 # Backend source code
│   ├── alembic/             # Alembic migration configuration
│   │   └── versions/        # Migration scripts
│   ├── src/                 # Python source code
│   │   ├── api/v1/          # API version 1 endpoints
│   │   ├── application/     # Use cases (to be implemented in later slices)
│   │   ├── domain/          # Pure domain models (entities, events, value objects)
│   │   ├── infrastructure/  # External services (DB, storage, queue, plugins)
│   │   │   ├── db/          # Database repository implementations
│   │   │   ├── storage/     # MinIO client
│   │   │   ├── queue/       # Redis client
│   │   │   └── plugins/     # Pipeline stage plugins (e.g., OCR)
│   │   ├── pipeline/        # Pipeline orchestrator and stage contracts
│   │   │   └── stages/      # Individual pipeline stages (to be implemented)
│   │   └── config.py        # Application configuration
│   ├── tests/               # Test suite (unit, integration, contract)
│   ├── Dockerfile           # Backend containerization
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (see below)
├── frontend/                # Frontend source code
│   ├── public/              # Static assets (index.html, favicon)
│   │   └── index.html
│   ├── src/                 # TypeScript source code
│   │   ├── main.tsx         # Entry point
│   │   └── App.tsx          # Root component
│   ├── Dockerfile           # Frontend containerization
│   ├── package.json         # Node.js dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   └── vite.config.ts       # Vite configuration
├── docs/                    # Documentation
│   ├── SRS.md               # Original requirements
│   ├── product.md           # Detailed product vision
│   ├── ARCHITECTURE.md      # v1 Architecture specification
│   └── ROADMAP.md           # Future feature roadmap
├── docker-compose.yml       # Service orchestration
└── README.md
```

## Installation & Usage

### Prerequisites
- Docker Engine (version 20.10+)
- Docker Compose (v2 plugin or standalone)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/Aditya0850/BlackBox.git
   cd BlackBox
   ```

2. Build and start all services:
   ```bash
   docker compose up --build
   ```
   This will:
   - Start PostgreSQL, MinIO, and Redis containers
   - Build and start the backend (FastAPI) container
   - Build and start the frontend (React/Vite) container
   - Apply database migrations (creating schemas and roles)
   - Create the MinIO evidence bucket if it doesn't exist

3. Wait for all services to become healthy (check docker compose logs).

### Verification
Once all services are running, verify the following:

1. **Backend Health Check**
   ```bash
   curl -s http://localhost:8000/health
   ```
   Expected response (when all dependencies are healthy):
   ```json
   {
     "status": "ok",
     "checks": {
       "postgres": "ok",
       "redis": "ok",
       "minio": "ok"
     }
   }
   ```

2. **Frontend Access**
   Open your browser to http://localhost:3000
   You should see a minimal BlackBox frontend with a header.

3. **Backend API Documentation**
   Visit http://localhost:8000/docs for the automatically generated OpenAPI/Swagger UI.

4. **Database Verification**
   Connect to PostgreSQL (using any client) and verify:
   - The `intel` and `audit` schemas exist
   - The roles `blackbox_app` and `audit_writer` exist
   - No tables have been created yet (tables will be added in later slices)

5. **MinIO Verification**
   Access the MinIO console at http://localhost:9001 (login with `minioadmin` / `minioadmin`)
   Verify that the `evidence` bucket exists.

6. **Redis Verification**
   Use `redis-cli` to ping the Redis container:
   ```bash
   docker exec -it blackbox_redis redis-cli ping
   ```
   Should return `PONG`.

### Environment Variables
The backend expects a `.env` file in the `backend/` directory. A sample is provided below (already included in the repository):

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_SERVER=db
POSTGRES_PORT=5432
POSTGRES_DB=blackbox

MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=evidence
MINIO_SECURE=false

REDIS_HOST=redis
REDIS_PORT=6379
```

These values match the service names used in `docker-compose.yml`.

## API/Backend Details

### Health Check Endpoint
- **URL**: `GET /health`
- **Description**: Performs real-time checks of all critical dependencies:
  - PostgreSQL: Executes `SELECT 1` and verifies that `intel` and `audit` schemas exist
  - Redis: Sends a `PING` command
  - MinIO: Verifies connectivity and ensures the `evidence` bucket exists (creates it if missing)
- **Response**:
  - `200 OK`: All dependencies are healthy
  - `503 Service Unavailable`: One or more dependencies are unhealthy, with details in the response body

### Current API Status
As this is Slice 1 (foundation), no feature endpoints have been implemented yet. The API is ready to accept routes in the `/api/v1` namespace. Future slices will add endpoints for case management, evidence upload, etc.

## Development Notes
- The backend is configured to reload on code changes (via volume mount in docker-compose)
- The frontend is configured for hot module replacement (HMR) via Vite
- Database migrations are managed with Alembic. To create a new migration:
  ```bash
  docker compose exec backend alembic revision -m "description"
  ```
  Then apply it with:
  ```bash
  docker compose exec backend alembic upgrade head
  ```

## Future Improvements
See [ROADMAP.md](docs/ROADMAP.md) for the planned v2+ features, including:
- Entity & Relationship Extraction
- Knowledge Graph
- Dynamic Timeline Reconstruction
- Investigation Notebook
- AI Suggestions
- Similarity Engine
- Cross-Case Intelligence
- Modus Operandi Detection
- Contradiction Detection
- Provenance Graph
- Decision Objects
- Truth & Uncertainty Engine
- Investigation Health Dashboard
- Predictive Investigation Suggestions

Each feature will be implemented in a vertical slice, following the same foundation-layers-feature approach.

---
*This README documents Slice 1: Project Foundation. As the platform evolves, this file will be updated to reflect the current state of the system.*