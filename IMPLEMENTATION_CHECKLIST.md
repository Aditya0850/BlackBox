# BlackBox Implementation Checklist for SIH 2026 PS 26189

Based on authoritative corrections from architecture review, this checklist shows the exact work needed to implement the core intelligence layer.

## 1. CURRENT-STATE ASSESSMENT

### What's Working (Forensic Spine)
- Case management CRUD (`backend/src/api/v1/cases.py`)
- Evidence management CRUD (`backend/src/api/v1/evidence.py`)
- OCR stage (`backend/src/pipeline/stages/ocr_stage.py`) - Real Tesseract
- Metadata extraction (`backend/src/pipeline/stages/metadata_extraction.py`) - Real EXIF/GPS/timestamps
- Pipeline architecture (`backend/src/pipeline/orchestrator.py`) - Clean PipelineStage protocol
- Demo dataset with ground truth (`demo_data_v2/ground_truth/CANONICAL_ENTITIES_AND_RELATIONSHIPS.json`)

### What Needs Replacement/Rework
- Entity extraction (`backend/src/pipeline/stages/entity_extraction.py`) - Rule-based regex only, no persistence
- Relationship extraction - Same file, proximity-heuristic only, not persisted
- AI summary stage - Fake (accepts `llm_client` but never calls LLM)
- Frontend - Placeholder (`frontend/src/App.tsx` - 15 lines wired to nothing)
- Knowledge graph storage - Missing `intel.entities`, `intel.entity_relationships` tables

## 2. FILES TO CREATE

### Database & Migration
- `backend/alembic/versions/<timestamp>_add_intelligence_tables.py` - Migration for new tables
- `backend/src/infrastructure/db/repositories/entity_repository.py`
- `backend/src/infrastructure/db/repositories/relationship_repository.py`
- `backend/src/infrastructure/db/repositories/mention_repository.py`
- `backend/src/infrastructure/db/repositories/relationship_evidence_repository.py`
- `backend/src/infrastructure/db/repositories/pattern_finding_repository.py`

### Pipeline Stages
- `backend/src/pipeline/stages/entity_resolution_stage.py`
- `backend/src/pipeline/stages/relationship_extraction_stage.py`
- `backend/src/pipeline/stages/graph_analytics_stage.py`
- `backend/src/pipeline/stages/pattern_detection_stage.py`
- `backend/src/pipeline/stages/nl_query_stage.py` (stretch - only if core solid)
- `backend/src/pipeline/stages/llm_entity_extraction_fallback.py` (stretch - only if core solid)
- `backend/src/pipeline/stages/llm_relationship_extraction_fallback.py` (stretch - only if core solid)

### API Endpoints
- `backend/src/api/v1/analysis.py` - New module for analysis endpoints

### Frontend Components
- `frontend/src/components/GraphView.tsx`
- `frontend/src/components/EntityDetailPanel.tsx`
- `frontend/src/components/RelationshipDetailPanel.tsx`
- `frontend/src/components/PatternAlerts.tsx`
- `frontend/src/components/TimelineView.tsx`

### Scripts & Tests
- `backend/scripts/validate_ground_truth.py` - Hermes-led validation script
- `backend/tests/pipeline/stages/test_entity_extraction.py`
- `backend/tests/pipeline/stages/test_entity_resolution.py`
- `backend/tests/pipeline/stages/test_relationship_extraction.py`
- `backend/tests/pipeline/stages/test_graph_analytics.py`
- `backend/tests/pipeline/stages/test_pattern_detection.py`
- `backend/tests/integration/test_intelligence_pipeline.py`
- `backend/tests/api/test_analysis_endpoints.py`
- `backend/tests/api/test_graph_endpoints.py`

## 3. FILES TO MODIFY

### Database Models
- `backend/src/infrastructure/db/models.py` - Add SQLAlchemy models for new tables

### Pipeline Orchestrator
- `backend/src/pipeline/orchestrator.py` - Update to include new stages in correct order

### Entity Extraction (Replace Entirely)
- `backend/src/pipeline/stages/entity_extraction.py` - Replace rule-based regex with deterministic extraction (regex + spaCy NER + dependency parsing)

### Frontend
- `frontend/src/App.tsx` - Replace placeholder with real layout incorporating new components
- `frontend/src/index.css` or similar - Add styles for new components if needed

## 4. ALEMBIC/DATABASE MIGRATIONS

### New Tables to Create (in migration file):

```sql
-- intel.entities: Canonical entities with metadata for disambiguation
CREATE TABLE intel.entities (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    entity_type VARCHAR(20) NOT NULL, -- person, phone, vehicle, location, organization
    canonical_value TEXT NOT NULL, -- Normalized form (e.g., "Rajesh Kumar")
    normalized_key VARCHAR(255) NOT NULL, -- For blocking: lowercase, stripped canonical_value
    entity_metadata JSONB, -- {aliases: [...], phones: [...], addresses: [...]}
    resolution_confidence FLOAT DEFAULT 0.0, -- Confidence in this being a resolved entity
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(case_id, entity_type, normalized_key)
);

-- intel.entity_mentions: Many-to-many link between entities and source evidence WITH OFFSETS
CREATE TABLE intel.entity_mentions (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    entity_id UUID NOT NULL REFERENCES intel.entities(id),
    finding_id UUID NOT NULL REFERENCES intel.findings(id),
    source_text TEXT NOT NULL, -- Exact text where entity appeared
    text_start_offset INTEGER NOT NULL, -- Character offset in source text
    text_end_offset INTEGER NOT NULL, -- Character offset in source text
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- intel.relationships: Evidence-backed relationships
CREATE TABLE intel.relationships (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    subject_entity_id UUID NOT NULL REFERENCES intel.entities(id),
    predicate VARCHAR(50) NOT NULL, -- calls, lives_at, owns, transfers_money_to, etc.
    object_entity_id UUID NOT NULL REFERENCES intel.entities(id),
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- intel.relationship_evidence: Provenance for relationships
CREATE TABLE intel.relationship_evidence (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    relationship_id UUID NOT NULL REFERENCES intel.relationships(id),
    finding_id UUID NOT NULL REFERENCES intel.findings(id),
    source_text TEXT NOT NULL, -- Exact text supporting this relationship
    text_start_offset INTEGER NOT NULL,
    text_end_offset INTEGER NOT NULL,
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- intel.pattern_findings: Persisted suspicious pattern detections
CREATE TABLE intel.pattern_findings (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    pattern_type VARCHAR(50) NOT NULL, -- call-transfer-delivery, burner-phone, etc.
    description TEXT NOT NULL,
    entities_involved JSONB NOT NULL, -- Array of entity IDs involved
    evidence_trail JSONB NOT NULL, -- Array of {finding_id, source_text, confidence, offsets}
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    detected_at TIMESTAMP NOT NULL, -- When pattern occurred (from evidence)
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_entities_case_type ON intel.entities(case_id, entity_type);
CREATE INDEX idx_entities_normalized_key ON intel.entities(normalized_key);
CREATE INDEX idx_relationships_case ON intel.relationships(case_id);
CREATE INDEX idx_mentions_entity ON intel.entity_mentions(entity_id);
CREATE INDEX idx_mentions_finding ON intel.entity_mentions(finding_id);
CREATE INDEX idx_relationship_evidence_rel ON intel.relationship_evidence(relationship_id);
CREATE INDEX idx_pattern_findings_case ON intel.pattern_findings(case_id);
```

## 5. PIPELINE IMPLEMENTATION ORDER (EXACT SEQUENCE)

### Phase 1: Foundation (Days 1-3)
1. Create database migration for new tables
2. Add SQLAlchemy models for new tables
3. Create repository classes for new entities
4. Update orchestrator to call new stages (placeholder stubs)
5. **STOP**: Verify existing Slice 1 functionality still works

### Phase 2: Deterministic Extraction (Days 4-6)
1. Implement deterministic entity extraction stage (regex + spaCy NER + dep parsing)
2. Store mentions in `intel.entity_mentions` with offsets
3. **STOP**: Verify extraction works and mentions are stored correctly

### Phase 3: Entity Resolution (Days 7-8)
1. Implement entity resolution stage (blocking, similarity, merging with corroboration)
2. Update `intel.entities` and create new mentions
3. **STOP**: Run ground truth validation on entity extraction + resolution ONLY
4. **DO NOT PROCEED** if entity resolution F1 < 0.80

### Phase 4: Relationship Extraction (Days 9-10)
1. Implement deterministic relationship extraction stage (spaCy patterns + structured joins)
2. Store relationships and evidence with proper provenance
3. **STOP**: Run ground truth validation on entities + relationships
4. **DO NOT PROCEED** if relationship F1 < 0.70

### Phase 5: Graph Analytics & APIs (Days 11-12)
1. Implement graph analytics stage (NetworkX centrality/community detection)
2. Build `/graph` and `/analysis/influencers` endpoints
3. **STOP**: Verify graph output is correct and performant

### Phase 6: Pattern Detection (Days 13-14)
1. Implement 2 core pattern detectors (call-transfer-delivery, location reuse)
2. Store findings in `intel.pattern_findings`
3. Build `/analysis/patterns` endpoint

### Phase 7: Frontend Development (Days 15-18)
1. Build GraphView component with 2D force-directed graph
2. Build EntityDetailPanel and RelationshipDetailPanel with provenance
3. Build PatternAlerts and TimelineView components
4. Wire case/evidence views to real APIs
5. **STOP**: Verify end-to-end flow works with demo dataset

### Phase 8: Cross-case & Validation (Days 19-20)
1. Implement cross-case shared entity detection endpoint
2. Run full validation script (Hermes lead)
3. Generate validation report with metrics
4. **STOP**: Verify system meets minimum thresholds for demo

### Phase 9: Stretch Features (Only if Solid) (Days 21-22)
1. ONLY IF all core metrics are strong:
   - Add bounded verified LLM fallback
   - Add fixed-shape NL queries (3 predefined shapes only)
   - Add visual polish and demo rehearsal

### Phase 10: Demo Preparation (Days 23-24)
1. End-to-end Docker Compose smoke tests
2. Rehearse demo script exactly
3. Prepare talking points emphasizing explainability and evidence traceability
4. Finalize validation metrics for presentation

## 6. API ENDPOINTS

### Graph Endpoints (`backend/src/api/v1/analysis.py`)
- `GET /api/v1/cases/{id}/graph`
  - Returns: {nodes: [...], edges: [...], analytics: {...}}
  - Node: {id, label, type, group, size, metadata: {canonical_value, aliases, phones, addresses}, resolution_confidence: Float}
  - Edge: {id, source, target, label (predicate), width, style (solid/dashed/dotted), confidence: Float}

- `GET /api/v1/cases/{id}/analysis/influencers`
  - Returns: [{entity_id, rank, centrality_score, explanation: String, connections: Number, entity_type}]

- `GET /api/v1/cases/{id}/analysis/patterns`
  - Returns: [{id, type, description, entities_involved: Array, evidence_trail: Array, confidence: Float, detected_at: Timestamp}]

- `GET /api/v1/cases/{id}/analysis/cross-case`
  - Returns: [{entity_type, canonical_value, cases: [{case_id, case_number, evidence_trail: Array}]}]

- `POST /api/v1/cases/{id}/analysis/query` (stretch - only if core solid)
  - Body: {question: String}
  - Returns: {subgraph: {nodes: [...], edges: [...]}, explanation: String, evidence_trail: Array}
  - Only supports 3 predefined question shapes:
    1. "Who connects [Person A] and [Person B]?"
    2. "Who is the most central person in this case?"
    3. "Show me the financial network of [Person]"

## 7. FRONTEND COMPONENTS

### GraphView Component (`frontend/src/components/GraphView.tsx`)
- Uses 2D force-directed graph (react-force-graph or cytoscape.js)
- Node styling:
  - Color by entity_type: person(#3b82f6), phone(#10b981), vehicle(#f59e0b), location(#8b5cf6), organization(#ef4444)
  - Size scaled by betweenness centrality (min 10px, max 50px)
  - Label: truncated canonical_value (full on hover/tooltip)
- Edge styling:
  - Width scaled by relationship confidence (min 1px, max 5px)
  - Style: solid (≥0.7), dashed (0.4-0.7), dotted (<0.4)
- Interactions:
  - Hover node: Tooltip showing name, type, resolution confidence, aliases
  - Hover edge: Tooltip showing predicate, confidence, evidence count
  - Click node: Slide-in side panel with entity details
  - Click edge: Slide-in side panel with relationship details
  - Drag: Standard force-graph physics for exploration
  - Double-click center: Reset view

### EntityDetailPanel Component
```
Entity: [BOLD canonical_value]
Type: [entity_type] ──────── Resolution Confidence: [progress bar]

Aliases: [comma-separated list or "None"]
Phones: [comma-separated list or "None"]  
Addresses: [comma-separated list or "None"]

Connected To: [number] entities via [number] relationships

EVIDENCE TRAIL:
• "[excerpt text...]" (Finding #[id] - Confidence: 0.87 - Offset: [start-end])
• "[excerpt text...]" (Finding #[id] - Confidence: 0.92 - Offset: [start-end])
• "[excerpt text...]" (Finding #[id] - Confidence: 0.76 - Offset: [start-end])
```

### RelationshipDetailPanel Component
```
RELATIONSHIP: [BOLD predicate]
Confidence: [progress bar]

Subject: [entity_name] ([entity_type])
Object: [entity_name] ([entity_type])

SUPPORTING EVIDENCE (click to view source):
• "[excerpt...]" (Finding #[id] - Confidence: 0.89 - Offset: [start-end])
• "[excerpt...]" (Finding #[id] - Confidence: 0.75 - Offset: [start-end])
• "[excerpt...]" (Finding #[id] - Confidence: 0.91 - Offset: [start-end])
```

### PatternAlerts Component
- Color-coded cards from `/analysis/patterns` endpoint
- Red for high confidence (≥0.8), orange for medium (0.5-0.8)
- Each card shows: description, entities involved, evidence trail, confidence, detected timestamp

### TimelineView Component
- Extract dates/times from evidence where possible (OCR text, metadata)
- Group by case_id, display chronologically
- Hover: Show full evidence excerpt and source with offset highlighting
- Click: Jump to corresponding evidence in list

## 8. DEPENDENCIES

### Backend (Python) - Add to `backend/requirements.txt`:
```
spacy>=3.0.0
networkx>=3.0
python-Levenshtein>=0.2.0  # for fuzzy matching
```
- Post-install: `python -m spacy download en_core_web_sm`

### Frontend (JavaScript) - Add to `frontend/package.json`:
```
react-force-graph@1.x.x   # or cytoscape.js for 2D graph
```

## 9. TESTING REQUIREMENTS

### Unit Tests (For each new pipeline stage)
- `backend/tests/pipeline/stages/test_entity_extraction.py`
- `backend/tests/pipeline/stages/test_entity_resolution.py`
- `backend/tests/pipeline/stages/test_relationship_extraction.py`
- `backend/tests/pipeline/stages/test_graph_analytics.py`
- `backend/tests/pipeline/stages/test_pattern_detection.py`

### Integration Tests
- `backend/tests/integration/test_intelligence_pipeline.py` - Full pipeline flow

### API Tests
- `backend/tests/api/test_analysis_endpoints.py`
- `backend/tests/api/test_graph_endpoints.py`

### Contract Tests
- Maintain existing contract tests in `backend/tests/contract/`

### Adversarial Testing (Hermes Lead)
- Red herring resistance: Ensure system doesn't inflate scores for legitimate look-alikes
- Noise injection: Add irrelevant text, verify doesn't create false relationships
- Confounding entities: Test with multiple people sharing names, verify resolution uses phones/addresses
- Temporal confounding: Test impossible timelines don't create false causal relationships
- Source reliability: Verify official documents weighted higher than social media rumors

## 10. GROUND-TRUTH EVALUATION CHECKPOINT

### Validation Script (`backend/scripts/validate_ground_truth.py` - Hermes Lead)
1. Runs full pipeline on all evidence in `demo_data_v2`
2. Compares extracted entities against `CANONICAL_ENTITIES_AND_RELATIONSHIPS.json`
3. Calculates precision/recall/F1 by entity type:
   - True Positive: Extracted entity matches canonical entity (exact canonical_value match)
   - False Positive: Extracted entity not in ground truth
   - False Negative: Ground truth entity not extracted
4. Compares extracted relationships against ground truth:
   - True Positive: Subject-predicate-object match with evidence overlap
   - False Positive: Extracted relationship not in ground truth
   - False Negative: Ground truth relationship not extracted
5. Tests entity resolution accuracy:
   - % of aliases correctly merged vs. false merges
   - Measures: precision, recall, F1 for merger decisions
6. Validates pattern detection (after implementation):
   - % of ground truth suspicious patterns correctly flagged
   - False positive rate on legitimate activity (should be < 5%)
7. Measures end-to-end latency: evidence upload → graph visualization ready
8. Generates validation report with metrics for demo

### Required Metrics Before Proceeding to Graph/Frontend:
- Entity extraction: Precision/Recall/F1 by type
- Relationship extraction: Precision/Recall/F1 by predicate
- Entity resolution: Merger precision/recall/F1
- **DO NOT PROCEED** if core intelligence is materially broken (F1 < 0.70 for key metrics)

## 11. PROVENANCE REQUIREMENTS

Every graph claim must be traceable to source evidence:
```
Graph Node/Edge
    → intel.entity or intel.relationship record
    → intel.entity_mention(s) or intel.relationship_evidence
    → intel.finding record
    → intel.analysis_snapshot record
    → intel.evidence record (source document)
    → OCR text or metadata (exact location via offsets)
    → SHA256 hash of evidence file
```

### Implementation Details:
- Entity records: Store `entity_metadata` including source finding IDs (implicit via mentions)
- Relationship records: Store provenance in `intel.relationship_evidence` table with:
  - `finding_id` → links to source finding
  - `source_text` → exact supporting text
  - `text_start_offset`/`text_end_offset` → character positions in source text
  - `confidence_score` → confidence in this evidence
- Entity-mention table: Provides many-to-many link between entities and findings with offsets
- All findings already trace to snapshots → evidence (existing functionality)
- Frontend: Click node/edge shows source evidence excerpt with highlighting and ability to jump to exact text offsets

## 12. SLICE 1 COMPATIBILITY RISKS

### Low Risk Changes:
- Adding new database tables (backward compatible)
- Adding new pipeline stages (can be enabled/disabled via config)
- Adding new API endpoints (under `/analysis/` namespace)
- Adding new frontend components (doesn't affect existing pages)

### Medium Risk Changes:
- Modifying `entity_extraction.py` - replaces existing stage entirely
  - **Mitigation**: Ensure new stage produces compatible findings format for downstream stages
  - Current stage outputs to `context.metadata["extracted_entities"]` and `["extracted_relationships"]`
  - New stage should maintain this for compatibility OR update downstream stages to use new tables directly
- Adding repository layer - must ensure existing code still works
  - **Mitigation**: New repositories only used by new stages initially

### No Risk Changes:
- All new files under `backend/src/pipeline/stages/` for new stages
- All new files under `backend/src/infrastructure/db/repositories/` for new repositories
- All new files under `backend/src/api/v1/` for new endpoints
- All new frontend components
- All new migration files
- All new test files
- All new validation scripts

### Critical Path for Zero Regression:
1. Implement new tables and repositories (no existing code touches these)
2. Implement new pipeline stages (entity extraction, resolution, relationship extraction) - these run alongside existing stages
3. Update orchestrator to include new stages in correct order (after metadata extraction, before ai_summary)
4. Verify existing stages (OCR, metadata, ai_summary) still work and produce findings
5. Only after ground truth validation passes, consider removing/replacing ai_summary stage with real LLM summarization

## 13. EXACT DEFINITION OF DONE

The system is "done" for SIH MVP when ALL of the following are met:

### Core Intelligence Layer:
- [ ] Deterministic entity extraction working (regex + spaCy NER + dependency parsing)
- [ ] Entity resolution with blocking, similarity scoring, and contextual corroboration
- [ ] Deterministic relationship extraction (spaCy patterns + structured CDR/financial joins)
- [ ] All extractions persist to proper tables with provenance (mentions, relationship_evidence)
- [ ] Entity resolution requires contextual corroboration (no merging on name alone)
- [ ] Relationships operate ONLY on resolved canonical entities

### Ground-Truth Validation (Must Pass Before Graph/Frontend):
- [ ] Entity extraction F1 ≥ 0.75 for all types (person, phone, vehicle, location, org)
- [ ] Entity resolution merger F1 ≥ 0.80
- [ ] Relationship extraction F1 ≥ 0.65 for key predicates (calls, transfers_money_to, associated_with)
- [ ] Zero false merges on red herring entities in demo dataset
- [ ] End-to-end latency < 5 seconds per evidence item

### Graph Analytics & APIs:
- [ ] NetworkX graph construction with degree/betweenness centrality, PageRank, Louvain communities
- [ ] `/api/v1/cases/{id}/graph` endpoint returning correct nodes/edges JSON
- [ ] `/api/v1/cases/{id}/analysis/influencers` endpoint with ranked influencers + explanations
- [ ] Graph computations cached per case with 5-minute TTL

### Pattern Detection (2 Core Patterns):
- [ ] Call-transfer-delivery sequence detector working with evidence trails
- [ ] Location reuse at specific windows detector working with evidence trails
- [ ] `/api/v1/cases/{id}/analysis/patterns` endpoint returning pattern findings
- [ ] Pattern detection precision ≥ 0.70, recall ≥ 0.60 on demo dataset

### Frontend:
- [ ] 2D force-directed graph visualization (NOT 3D)
- [ ] Node/edge styling by type/confidence as specified
- [ ] Click-to-evidence-trace functionality working
- [ ] Entity detail panel showing aliases, phones, addresses, source evidence with offsets
- [ ] Relationship detail panel showing predicate, confidence, supporting evidence with offsets
- [ ] Pattern alerts component displaying detected patterns
- [ ] Timeline view showing chronological events with evidence sources
- [ ] Case/evidence views wired to real APIs

### Cross-case Intelligence:
- [ ] `/api/v1/cases/{id}/analysis/cross-case` endpoint working
- [ ] Returns shared entities (≥2 cases) with evidence trails

### Stretch Features (Only if Core is Solid):
- [ ] Bounded verified LLM fallback (every proposal verified against source text)
- [ ] Fixed-shape NL queries (3 predefined shapes only)
- [ ] Visual polish and demo rehearsal complete

### Demo Readiness:
- [ ] End-to-end Docker Compose smoke tests pass morning and evening
- [ ] Demo script rehearsed exactly with timing
- [ ] Validation report printed with metrics for judges
- [ ] Talking points emphasizing explainability: "every claim traces back to evidence"
- [ ] System correctly ignores planted red herrings in demo dataset

## 14. FEATURE CLASSIFICATION

### MUST HAVE (Implement All for SIH MVP)
1. Persistent canonical entity storage (`intel.entities` table)
2. Entity resolution/disambiguation with confidence scoring and contextual corroboration
3. Evidence-backed relationship storage (`intel.relationships` table)
4. Relationship provenance storage (`intel.relationship_evidence` table with offsets)
5. Entity mention storage (`intel.entity_mentions` table with offsets)
6. Deterministic entity extraction (regex + spaCy NER + dependency parsing)
7. Deterministic relationship extraction (spaCy dependency patterns + structured joins)
8. NetworkX graph analytics (degree/betweenness centrality, PageRank, community detection)
9. Graph API endpoints (`/graph`, `/analysis/influencers`)
10. Two core pattern detectors (call-transfer-delivery, location reuse)
11. Pattern persistence (`intel.pattern_findings` table)
12. Pattern API endpoint (`/analysis/patterns`)
13. Cross-case shared entity detection via SQL joins
14. Frontend 2D graph visualization with click-to-evidence-trace
15. Entity detail panel with provenance (azioaes, phones, addresses, source evidence)
16. Relationship detail panel with provenance (predicate, confidence, supporting evidence)
17. Ground-truth evaluation framework and validation script
18. Exact evidence provenance from graph claims to source text with character offsets

### SHOULD HAVE (Implement if MUST HAVEs Complete Early)
1. Temporal relationship timestamps (extract dates/times from evidence text)
2. Uncertainty visualization in graph (dashed lines for low-confidence edges)
3. Timeline view of events extracted from evidence (chronological)
4. Simple contradiction detector (same phone used by two "different" people)
5. Evidence confidence scoring by source type (FIR > CDR > social media > witness)
6. Export graph as JSON/CSV for external analysis
7. Basic authentication layer (placeholder username/password for demo)

### WOW FEATURES (Only Attempt if ALL MUST HAVEs and SHOULD HAVEs Complete)
1. "Show me similar patterns" button finding entities with similar connection profiles
2. Anomaly detection highlighting: impossible travel times, sudden relationship formation
3. Cross-case temporal alignment showing correlated activities across cases
4. Model confidence calibration showing precision/recall against ground truth

### POST-HACKATHON Features (Explicitly Deferred)
1. Millions of records: partitioned tables, async workers, message queue
2. Streaming data: Kafka consumers for live CDR/financial feeds
3. Temporal knowledge graphs: edges with valid-time intervals, temporal queries
4. Advanced entity resolution: ML-based embedding similarity + rule-based constraints
5. OSINT ingestion: web scraping, social media APIs, dark web monitoring
6. Financial analysis: flow detection, shell company detection, Benford's law
7. Call Detail Record (CDR) analysis: cell tower triangulation, frequent contact detection
8. Multilingual NLP: Hindi/regional language support for Indian law enforcement context
9. Secure/offline deployment: air-gapped variant with local LLM models
10. Model evaluation framework: A/B testing different LLMs, continuous retraining
11. Open-ended natural language queries (only 2-3 fixed shapes if implemented as stretch)
12. 3D graph visualization (strictly 2D as required)
13. Real-time streaming simulation
14. Voice-to-query investigator interface
15. Voice-to-query investigator interface

**STOP - Awaiting your approval before proceeding with implementation.**