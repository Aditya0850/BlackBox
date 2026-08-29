# BlackBox - AI-Powered Criminal Network Analysis System (SIH 26189)

> **Note**: This repository contains the foundation (Slice 1) of the BlackBox platform, which sets up the core infrastructure for an AI-powered evidence management and investigative intelligence platform. The project also includes synthetic dataset generation capabilities for demonstrating and validating the system as part of the SIH 26189 problem statement.

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [Development Guidelines](#development-guidelines)
- [Documentation](#documentation)
- [Verification & Testing](#verification--testing)
- [Future Roadmap](#future-roadmap)
- [License](#license)

## Overview

BlackBox is designed to transform raw digital evidence into structured, actionable intelligence. The platform automatically ingests, analyzes, and correlates diverse evidence types (documents, images, videos, audio, financial records, call logs, social media, etc.) to reveal hidden connections, patterns, and investigative leads—all while maintaining explainable AI principles and robust audit trails.

This repository delivers:
- **Slice 1 (Foundation)**: Core infrastructure including backend API, database, storage, queue, and frontend shell.
- **Synthetic Data Generation**: Tools and scripts to generate realistic criminal network datasets (20K+ records) for testing and demonstration.
- **Comprehensive Documentation**: Architecture, product vision, API specifications, and implementation plans.

## Key Features

### Core Platform Capabilities
- **Evidence Ingestion**: Secure upload and storage of diverse evidence formats
- **AI-Powered Understanding**: Automatic extraction of entities, relationships, timelines, and insights from evidence
- **Explainable AI**: Every AI conclusion includes confidence scores, supporting/contradicting evidence, source references, and human-verifiable reasoning
- **Case Management**: Organize investigations with victims, suspects, witnesses, evidence, timelines, and reports
- **Cross-Case Intelligence**: Discover patterns and connections across multiple investigations using modus operandi, behavioral analysis, and geographic profiling
- **Audit & Compliance**: Immutable audit logs with role-based access control and GDPR-ready design
- **Real-Time Collaboration**: Multi-user support with change tracking and notifications

### Technical Foundation (Slice 1)
- **Clean Architecture Backend**: Separation of concerns with distinct layers (API, Application, Domain, Infrastructure, Pipeline)
- **Domain-Driven Design**: Clear bounded contexts with PostgreSQL schemas for `intel` (machine knowledge) and `audit` (append-only logs)
- **Event-Driven Pipeline**: Extensible evidence processing pipeline for OCR, AI analysis, and enrichment
- **Resilient Infrastructure**: PostgreSQL 15, MinIO (S3-compatible storage), Redis 7 for queuing
- **Production-Ready DevOps**: Docker Compose orchestration with health checks, volume mounts for hot reloading, and environment-based configuration
- **Automated Database Migrations**: Alembic for schema version control
- **Interactive API Documentation**: Auto-generated OpenAPI/Swagger UI at `/docs`
- **Health Monitoring**: Real-time verification endpoint checking all critical dependencies

## System Architecture

### High-Level Components
```plaintext
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend App  │    │   Backend API    │    │  Infrastructure │
│ (React/Vite/TS) │◄──►│ (FastAPI/Python) │◄──►│ (PostgreSQL,    │
└─────────────────┘    └──────────────────┘    │  MinIO, Redis)  │
        │                     │               └─────────────────┘
        │                     │
        ▼                     ▼
┌─────────────────┐    ┌──────────────────┐
│  Evidence Upload│    │  Processing      │
│   & Management  │    │  Pipeline        │
└─────────────────┘    └──────────────────┘
```

### Backend Layers (Clean Architecture)
1. **API Layer** (`backend/src/api/`): HTTP endpoints, request/response handling, dependency injection
2. **Application Layer** (`backend/src/application/`): Use cases orchestrating business logic
3. **Domain Layer** (`backend/src/domain/`): Pure business models (entities, events, value objects) - zero framework dependencies
4. **Infrastructure Layer** (`backend/src/infrastructure/`): External service implementations (database repositories, storage clients, queue clients, plugins)
5. **Pipeline Layer** (`backend/src/pipeline/`): Evidence processing orchestrator and stage contracts

### Data Architecture
- **PostgreSQL Schemas**:
  - `intel.*`: Machine-generated knowledge (OCR results, entity extractions, AI summaries, relationships)
  - `audit.*`: Append-only audit log (no UPDATE/DELETE permissions - write-only for integrity)
  - `notebook.*`: Reserved for future human-authored content (Investigation Notebook)
- **Storage**: MinIO bucket for raw evidence files (images, videos, documents, etc.)
- **Queue**: Redis for asynchronous pipeline job distribution (planned for Slice 2+)

### API Conventions
- **Versioning**: All endpoints under `/api/v1`
- **Audit Requirements**: Mutating endpoints (POST, PUT, PATCH, DELETE) require a `reason` field for audit logging
- **Error Format**: Standardized `{ error: { code, message, details } }`
- **Pagination**: Cursor-based for list endpoints
- **Documentation**: Interactive Swagger UI at `/docs`, ReDoc at `/redoc`

## Technology Stack

| Layer          | Technology                            | Version/Details                     |
|----------------|---------------------------------------|-------------------------------------|
| **Backend**    | Python                                | 3.12                                |
|                | FastAPI                               | Modern, async web framework         |
|                | SQLAlchemy 2.0                        | ORM with async support              |
|                | Alembic                               | Database migration tool             |
|                | Pydantic                              | Settings management & data validation |
| **Database**   | PostgreSQL                            | 15                                  |
| **Storage**    | MinIO                                 | S3-compatible object storage        |
| **Queue**      | Redis                                 | 7 (for pipeline workers)            |
| **Frontend**   | TypeScript                            |                                     |
|                | React                                 | 18                                  |
|                | Vite                                  | Build tool with HMR                 |
| **DevOps**     | Docker                                | Containerization                    |
|                | Docker Compose                        | Multi-service orchestration         |
|                | GitHub Actions                        | CI/CD (planned)                     |

## Getting Started

### Prerequisites
- Docker Engine (version 20.10+)
- Docker Compose (v2 plugin or standalone)
- Git (to clone the repository)

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Aditya0850/BlackBox.git
   cd BlackBox
   ```

2. **Build and start all services**:
   ```bash
   docker compose up --build
   ```
   This command will:
   - Start PostgreSQL, MinIO, and Redis containers
   - Build and start the backend (FastAPI) container
   - Build and start the frontend (React/Vite) container
   - Apply database migrations (creating schemas and roles)
   - Create the MinIO `evidence` bucket on backend startup if missing

3. **Wait for services to become healthy**:
   Monitor logs with `docker compose logs -f` or check individual service health.

### Verification

Once all services are running, verify the following:

#### 1. Backend Health Check
```bash
curl -s http://localhost:8000/health
```
Expected response when healthy:
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

#### 2. Frontend Access
Open your browser to [http://localhost:3000](http://localhost:3000)
You should see the BlackBox frontend interface.

#### 3. API Documentation
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### 4. Database Verification
Connect to PostgreSQL (using any client) and verify:
- The `intel` and `audit` schemas exist
- Roles `blackbox_app` and `audit_writer` exist
- No application tables created yet (tables added in later slices)

#### 5. MinIO Verification
Access MinIO console at [http://localhost:9001](http://localhost:9001) (login: `minioadmin` / `minioadmin`)
Verify the `evidence` bucket exists.

#### 6. Redis Verification
```bash
docker exec -it blackbox_redis redis-cli ping
```
Should return `PONG`.

### Dependency Failure Testing
To verify the health check correctly reports failures, stop a dependency and check the endpoint:

```bash
# Stop Redis
docker compose stop redis
# Check health endpoint (should return 503)
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health
# View details
curl -s http://localhost:8000/health
```

## Project Structure

```
blackbox/
├── backend/                 # Backend source code (Python/FastAPI)
│   ├── alembic/             # Alembic migration configuration
│   │   └── versions/        # Migration scripts
│   ├── src/                 # Python source code
│   │   ├── api/             # API layer (routers, dependencies)
│   │   │   └── v1/          # API version 1 endpoints
│   │   ├── application/     # Use cases (business logic orchestration)
│   │   ├── domain/          # Pure domain models (entities, events, value objects)
│   │   ├── infrastructure/  # External service implementations
│   │   │   ├── db/          # Database repository implementations
│   │   │   ├── storage/     # MinIO client
│   │   │   ├── queue/       # Redis client
│   │   │   └── plugins/     # Pipeline stage plugins (OCR, NLP, etc.)
│   │   ├── pipeline/        # Pipeline orchestrator and stage contracts
│   │   └── config.py        # Application configuration (Pydantic settings)
│   ├── tests/               # Test suite (unit, integration, contract)
│   ├── Dockerfile           # Backend containerization
│   ├── requirements.txt     # Python dependencies
│   └── .env                 # Environment variables (see below)
├── frontend/                # Frontend source code (React/Vite/TypeScript)
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
│   ├── ARCHITECTURE.md      # Detailed system architecture
│   ├── product.md           # Product vision and philosophy
│   ├── SRS.md               # Original requirements specification
│   ├── ROADMAP.md           # Future feature roadmap
│   ├── README.md            # Original foundation documentation
│   └── *.md                 # Additional plans and reports
├── demo_data/               # Sample datasets for testing
├── demo_data_v2/            # Alternative dataset version
├── Images/                  # Image assets
├── docker-compose.yml       # Service orchestration
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

## Development Guidelines

### Backend Commands
- **Run backend**: `docker compose up backend` or `docker compose up` (starts all services)
- **Run migrations**: `docker compose exec backend alembic upgrade head`
- **Create migration**: `docker compose exec backend alembic revision -m "description"`
- **Run tests**: `docker compose exec backend pytest`
- **Run specific test**: `docker compose exec backend pytest path/to/test.py::test_function`
- **Run unit tests**: `docker compose exec backend pytest backend/tests/unit/`
- **Run integration tests**: `docker compose exec backend pytest backend/tests/integration/`
- **Run contract tests**: `docker compose exec backend pytest backend/tests/contract/`
- **Backend development mode**: `docker compose up backend` (auto-reloads on code changes via volume mount)

### Frontend Commands
- **Run frontend**: `docker compose up frontend` or `docker compose up` (starts all services)
- **Frontend dev server**: Available at http://localhost:3000 with HMR
- **Install frontend dependencies**: `docker compose run --rm frontend npm ci`
- **Build frontend**: `docker compose run --rm frontend npm run build`
- **Preview build**: `docker compose run --rm frontend npm run preview`

### General Commands
- **Start all services**: `docker compose up`
- **Start all services in background**: `docker compose up -d`
- **Stop all services**: `docker compose down`
- **View logs**: `docker compose logs -f [service_name]`
- **Rebuild and restart**: `docker compose up --build`

### Environment Configuration
The backend expects a `.env` file in the `backend/` directory. The repository includes a sample:

```env
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

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Detailed technical architecture
- [product.md](docs/product.md) - Product vision, philosophy, and feature descriptions
- [SRS.md](docs/SRS.md) - Original requirements specification
- [ROADMAP.md](docs/ROADMAP.md) - Planned future features and releases
- [README.md](docs/README.md) - Original foundation documentation (Slice 1)
- Additional planning documents:
  - [ADVERSARIAL_TEST_PLAN.md](ADVERSARIAL_TEST_PLAN.md)
  - [EVALUATION_HARNESS_PLAN.md](EVALUATION_HARNESS_PLAN.md)
  - [FINAL_IMPLEMENTATION_PLAN.md](FINAL_IMPLEMENTATION_PLAN.md)
  - [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)
  - [STRATEGY_REPORT.md](STRATEGY_REPORT.md)
  - [VALIDATION_COMMANDS.md](VALIDATION_COMMANDS.md)
  - [WINNING_PLAN.md](WINNING_PLAN.md)

## Verification & Testing

### Test Suites
The project includes a comprehensive test suite:
- **Unit Tests**: `backend/tests/unit/`
- **Integration Tests**: `backend/tests/integration/`
- **Contract Tests**: `backend/tests/contract/`

Run all tests:
```bash
docker compose exec backend pytest
```

Run with coverage (if configured):
```bash
docker compose exec backend pytest --cov=backend
```

### Synthetic Data Generation
The repository includes tools for generating synthetic criminal network datasets:

1. **Generation Scripts**: Located in `demo_data/generation_scripts/`
   - `generate_financial_transactions.py`
   - `generate_cdr_records.py`
   - `generate_fir_documents.py`
   - `generate_witness_statements.py`
   - `generate_social_media_intelligence.py`
   - `generate_surveillance_records.py`
   - `generate_world_model.py`
   - `generate_clean_world.py`
   - `generate_fixed_world.py`

2. **Validation**: Validate generated data with:
   - `demo_data/generation_scripts/validate_full.py`
   - `demo_data/generation_scripts/validate_test.py`

3. **Dataset Locations**:
   - Generated JSON datasets: `demo_data/generation_scripts/demo_data/full_dataset/<category>/`
   - Processed datasets: `demo_data/` and `demo_data_v2/`

## Future Roadmap

See [ROADMAP.md](docs/ROADMAP.md) for the complete planned feature set, including:

- **Entity & Relationship Extraction**
- **Knowledge Graph Construction**
- **Dynamic Timeline Reconstruction**
- **Investigation Notebook (Human-Authored Content)**
- **AI-Powered Investigative Suggestions**
- **Similarity Engine (Cross-Case Analysis)**
- **Modus Operandi Detection**
- **Contradiction Detection**
- **Provenance Graph Tracking**
- **Decision Objects & Reasoning Traces**
- **Truth & Uncertainty Engine**
- **Investigation Health Dashboard**
- **Predictive Investigation Analytics**

Each feature is planned as a vertical slice, following the same foundation-layers-feature approach introduced in Slice 1.

## License

This project is proprietary and confidential. All rights reserved.

---
*This README documents the current state of the BlackBox platform. As the system evolves through additional slices, this file will be updated to reflect new features, architectural changes, and usage guidelines.*

Last updated: August 2026