# BlackBox — v1 Architecture

> BlackBox is not an AI system that stores evidence. It is a forensic
> knowledge system that preserves, explains, and evolves investigative
> knowledge while maintaining complete trust, provenance, and historical
> integrity.

Status: v1 build target. This document specifies **what the system is
built on** — a 10-year-compatible foundation for a v1 scoped to: Case
Management, Evidence Management, Metadata Extraction, OCR, AI Summaries,
Chain of Custody, Search, Timeline, Reporting.

Deferred user-facing capabilities (Knowledge Graph, Similarity Engine,
Investigation Notebook, Trust Engine, etc.) live in `ROADMAP.md`, not
here. This document contains only what v1 needs to implement PLUS the
extension points that are foundational and cheap to keep now — not
speculative feature scaffolding.

---

## 1. Principles (kept — governs everything else)

1. Every AI claim must be traceable to source evidence. No unsupported statements.
2. "Unknown" is a valid, preferred answer over a guess. Confidence is calibrated, not fabricated.
3. Humans remain in control. AI proposes; investigators dispose.
4. Every action on evidence is auditable forever.
5. Interfaces are stable; implementations behind them are expected to evolve.
6. Nothing is ever lost: replace → new version; edit → append; delete → archive.

---

## 2. High-Level Architecture

```
                    ┌─────────────────────┐
                    │   React Frontend    │
                    └──────────┬──────────┘
                               │ REST /api/v1
                    ┌──────────▼──────────┐
                    │     FastAPI API     │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
      ┌───────▼──────┐ ┌───────▼──────┐ ┌────────▼───────┐
      │  PostgreSQL  │ │    MinIO     │ │  Redis (queue) │
      │ intel schema │ │ (evidence    │ │  + pipeline    │
      │ audit schema │ │  raw bytes)  │ │  worker pool   │
      └──────────────┘ └──────────────┘ └────────────────┘
```

Postgres is the single system of record. MinIO holds only raw evidence
bytes, addressed by hash. Redis is disposable — worst case on loss is
re-queuing jobs, never data loss.

**Note on schemas:** `intel` and `audit` are both built in v1. A
`notebook` schema is reserved (empty) — see §5, Human/Machine separation
— but no notebook tables are created until Investigation Notebook is
in scope (ROADMAP.md).

---

## 3. Clean Architecture Boundaries (kept)

```
api/            → HTTP layer only. No business logic.
application/    → Use cases (CreateCaseUseCase, UploadEvidenceUseCase, ...)
domain/         → Pure models, no framework imports.
infrastructure/ → SQLAlchemy repos, MinIO client, Redis client, plugin impls.
pipeline/       → Stage plugins + orchestrator.
```

`domain/` never imports from `infrastructure/` or `api/`. This is what
lets a v1 OCR implementation be replaced later without touching anything
above `infrastructure/`.

---

## 4. Folder Structure

```
blackbox/
├── docker-compose.yml
├── backend/
│   ├── alembic/
│   ├── src/
│   │   ├── api/v1/
│   │   │   ├── cases.py
│   │   │   ├── evidence.py
│   │   │   └── audit.py
│   │   ├── application/
│   │   │   ├── cases/
│   │   │   ├── evidence/
│   │   │   └── audit/
│   │   ├── domain/
│   │   │   ├── entities/
│   │   │   ├── events/
│   │   │   └── value_objects/
│   │   ├── infrastructure/
│   │   │   ├── db/
│   │   │   ├── storage/
│   │   │   ├── queue/
│   │   │   └── plugins/
│   │   │       └── ocr/          # v1: TesseractOCRProvider
│   │   ├── pipeline/
│   │   │   ├── contracts.py      # EvidenceContext, PipelineStage, StageExecutionRecord
│   │   │   ├── orchestrator.py
│   │   │   └── stages/           # v1: integrity_check, metadata_extract, ocr, ai_summary
│   │   └── config.py
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── contract/             # tests each plugin against its Protocol
└── frontend/
    └── src/
```

---

## 5. Human/Machine Separation (kept — foundational, cheap now)

Even though Investigation Notebook is deferred, the schema boundary that
will host it is decided now, because retrofitting a permission boundary
after data exists is expensive; reserving an empty schema costs nothing.

- `intel.*` — Machine Knowledge (all v1 tables live here).
- `audit.*` — append-only, no UPDATE/DELETE grant for any role, ever.
- `notebook.*` — reserved, empty in v1. When Investigation Notebook is
  built (ROADMAP), its tables go here with the pipeline worker's DB role
  having no grant on this schema at all.

This is the only "future" decision baked into v1: which schema new
human-authored tables will belong to, and that AI-writing-capable roles
never get a grant on it.

---

## 6. PostgreSQL Schema — v1

### 6.1 `intel.cases`
```sql
CREATE TABLE intel.cases (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           TEXT NOT NULL,
    status          TEXT NOT NULL CHECK (status IN ('open','closed','archived')),
    created_by      UUID NOT NULL REFERENCES users(id),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    tags            TEXT[] DEFAULT '{}'
);
CREATE INDEX idx_cases_status ON intel.cases(status);
CREATE INDEX idx_cases_tags ON intel.cases USING GIN(tags);
```

### 6.2 `intel.evidence`
```sql
CREATE TABLE intel.evidence (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    original_filename  TEXT NOT NULL,
    mime_type          TEXT NOT NULL,
    file_size_bytes    BIGINT NOT NULL,
    sha256_hash        TEXT NOT NULL UNIQUE,
    storage_location   TEXT NOT NULL,
    uploaded_by        UUID NOT NULL REFERENCES users(id),
    uploaded_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_evidence_hash ON intel.evidence(sha256_hash);
```

### 6.3 `intel.case_evidence` (many-to-many)
```sql
CREATE TABLE intel.case_evidence (
    case_id      UUID NOT NULL REFERENCES intel.cases(id),
    evidence_id  UUID NOT NULL REFERENCES intel.evidence(id),
    linked_by    UUID NOT NULL REFERENCES users(id),
    linked_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (case_id, evidence_id)
);
```
Kept many-to-many from the start — retrofitting this FK shape after
evidence rows exist is the expensive kind of change; specifying it now
costs nothing extra.

### 6.4 `intel.analysis_snapshots` (kept — the versioning backbone)
```sql
CREATE TABLE intel.analysis_snapshots (
    id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    evidence_id           UUID NOT NULL REFERENCES intel.evidence(id),
    pipeline_version      TEXT NOT NULL,
    plugin_versions       JSONB NOT NULL,   -- {"ocr": "tesseract-5.3"}
    trigger               TEXT NOT NULL CHECK (trigger IN
                            ('upload','manual_reanalysis','scheduled_reanalysis')),
    triggered_by          UUID REFERENCES users(id),
    is_current            BOOLEAN NOT NULL DEFAULT true,
    superseded_by         UUID REFERENCES intel.analysis_snapshots(id),
    investigator_approval TEXT CHECK (investigator_approval IN
                            ('pending','approved','rejected')) DEFAULT 'pending',
    created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_snapshot_evidence ON intel.analysis_snapshots(evidence_id);
CREATE UNIQUE INDEX idx_snapshot_current
    ON intel.analysis_snapshots(evidence_id) WHERE is_current;
```

### 6.5 `intel.findings`
```sql
CREATE TABLE intel.findings (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_id          UUID NOT NULL REFERENCES intel.analysis_snapshots(id),
    key                  TEXT NOT NULL,
    value                JSONB NOT NULL,
    confidence_level     TEXT NOT NULL CHECK (confidence_level IN
                           ('high','medium','low','unknown')),
    confidence_score     REAL NOT NULL,
    extraction_method    TEXT NOT NULL,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_findings_snapshot ON intel.findings(snapshot_id);
```
No `provenance.edges` table in v1 — findings reference their snapshot,
which references its evidence, which is sufficient lineage for v1's OCR
→ AI Summary chain. A generic provenance graph is ROADMAP (needed once
entities/relationships/theories exist and lineage crosses object types).

### 6.6 `audit.events` (append-only, kept as designed)
```sql
CREATE TABLE audit.events (
    id                 UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id            UUID REFERENCES users(id),
    evidence_id        UUID REFERENCES intel.evidence(id),
    case_id            UUID REFERENCES intel.cases(id),
    action             TEXT NOT NULL,   -- 'view','download','edit','delete','export','ai_analysis'
    previous_state     JSONB,
    new_state          JSONB,
    reason             TEXT,
    session_id         TEXT,
    ip_address         INET,
    device_info        TEXT,
    ai_pipeline_version TEXT,
    occurred_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_audit_evidence ON audit.events(evidence_id);
CREATE INDEX idx_audit_case ON audit.events(case_id);
CREATE INDEX idx_audit_occurred ON audit.events(occurred_at);
```
Postgres role with INSERT/SELECT only, granted to nothing else.

### 6.7 Reserved, not built in v1
`intel.entity_state_transitions`, `intel.entities`,
`intel.entity_relationships`, `provenance.edges`, `notebook.*` — all
ROADMAP. Not named as empty tables in v1's migrations; the schema
namespaces (`notebook`) are reserved, but no speculative tables are
created ahead of need.

---

## 7. AI Pipeline Interface (kept — this is the extension point that matters most)

```python
# pipeline/contracts.py

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Protocol, Any

class StageStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"

@dataclass
class StageExecutionRecord:
    stage_name: str
    status: StageStatus
    started_at: datetime
    finished_at: datetime | None
    model_version: str | None
    reason: str | None = None
    error_details: str | None = None

@dataclass
class Finding:
    key: str
    value: Any
    confidence_level: str
    confidence_score: float
    extraction_method: str

@dataclass
class EvidenceContext:
    evidence_id: str
    snapshot_id: str
    findings: list[Finding] = field(default_factory=list)
    execution_history: list[StageExecutionRecord] = field(default_factory=list)

    def add_finding(self, finding: Finding) -> None:
        self.findings.append(finding)

    def record_execution(self, record: StageExecutionRecord) -> None:
        self.execution_history.append(record)


class PipelineStage(Protocol):
    """A stage must NEVER fail silently — if it cannot complete, it still
    returns a context with a FAILED/SKIPPED StageExecutionRecord."""
    name: str
    def run(self, context: EvidenceContext) -> EvidenceContext: ...


class OCRProvider(Protocol):
    def extract_text(self, file_bytes: bytes, mime_type: str) -> list[Finding]: ...
```

**v1 pipeline stages (implemented):** Integrity Verification → Metadata
Extraction → OCR → AI Summary.

**Why this interface is worth keeping even though most of the roadmap's
plugins (NER, Similarity, Entity Extraction) aren't built yet:** the cost
of the `Protocol` + `EvidenceContext` contract is a few dozen lines of
code, written once. The cost of NOT having it — bolting a plugin
architecture onto four already-hardcoded pipeline stages later — is a
rewrite. This is the textbook case of "cheap now, expensive later,"
which is exactly the bar for staying in ARCHITECTURE.md rather than
ROADMAP.md.

---

## 8. API Conventions

- Versioned routes: `/api/v1/...`
- Mutating endpoints touching evidence require a `reason` field → `audit.events.reason`.
- Errors: `{ "error": { "code": "...", "message": "...", "details": {} } }`
- Cursor-based pagination.

---

## 9. Security & Audit Model

- RBAC: `investigator`, `admin`, `viewer`.
- Every evidence action writes `audit.events` synchronously before success.
- `audit.events`: no UPDATE/DELETE grant, ever.
- SHA-256 re-verified on download; mismatch blocks download, writes FAILED audit event.

---

## 10. v1 Milestone ("stabilize" definition)

1. `docker compose up` — FastAPI, PostgreSQL (`intel`/`audit` schemas +
   role grants), Redis, MinIO, health checks green.
2. Create/list/update Case.
3. Upload Evidence (image/PDF/DOCX/TXT) → hashed, stored, linked to case.
4. Every evidence action writes a correct `audit.events` row.
5. Pipeline runs Integrity → Metadata → OCR → AI Summary, producing a real
   `analysis_snapshot` with real `findings`.
6. Search over case/evidence metadata + OCR text (Postgres full-text).
7. Timeline view generated from extracted dates/findings.
8. Export a basic case report (evidence list, timeline, chain of custody).

This is v1. Once stable, evaluate ROADMAP.md for v2.
