# BlackBox Strategy Report: Building a Winning SIH 2026 Solution

## A. Verified Current State

### What's Actually Working (Forensic Spine)
✅ **Case Management**: Full CRUD operations with case numbering (CASE-YYYY-NNNNN), status tracking, tags
✅ **Evidence Management**: Upload, metadata extraction (EXIF/GPS), storage location tracking, hash verification
✅ **Chain of Custody**: Versioned analysis snapshots with investigator approval workflow, hash-verified
✅ **OCR**: Real Tesseract integration extracting text from images/PDFs
✅ **Metadata Extraction**: Real EXIF/GPS/timestamps from images, page counts from PDFs
✅ **Pipeline Architecture**: Clean, extensible PipelineStage protocol with orchestrator
✅ **Database**: PostgreSQL 15 with SQLAlchemy 2.0 ORM, Alembic migrations (though versions directory empty)
✅ **API**: FastAPI with automatic OpenAPI/Swagger docs at /docs
✅ **Tests**: ~1900 lines of unit/integration/contract tests foundation
✅ **Demo Dataset**: Genuinely strong with planted red herrings, aliases, multi-case entities in `demo_data_v2/ground_truth/CANONICAL_ENTITIES_AND_RELATIONSHIPS.json`

### What's Partially Working/Misrepresented
🟡 **Entity Extraction**: Exists but rule-based regex only, no persistence layer, struggles with aliases/variations
🟡 **Relationship Extraction**: Proximity-heuristic only, not persisted to database
🟡 **AI Summary**: Fake - accepts `llm_client` parameter but never calls LLM, pure keyword matching
🟡 **Frontend**: 15-line placeholder wired to nothing

### What's Completely Missing (Intelligence Layer)
❌ **Knowledge Graph Storage**: No `intel.entities` or `intel.entity_relationships` tables
❌ **Graph Visualization**: No frontend component, no `/graph` endpoint
❌ **Centrality Analysis**: No degree/betweenness centrality, PageRank, community detection
❌ **Cross-case Intelligence**: No shared entity detection across cases
❌ **Contradiction/Anomaly Detection**: No temporal conflict detection, impossible timelines
❨ **Investigator NL Query**: No natural language interface to graph
❨ **Entity Resolution**: No confidence-scored merging of aliases/variations (Rajesh Kumar vs R. Kumar)
❨ **Temporal Intelligence**: Relationships treated as timeless edges
❨ **Evidence Provenance**: Extracted entities not linked back to source findings/evidence
❨ **Confidence Model**: No meaningful confidence scoring for extraction/resolution/relationships

## B. PS 26189 Requirement Matrix

| Requirement | Current State | Required for Credible Solution | Final Implementation (1-2 weeks) |
|-------------|---------------|--------------------------------|----------------------------------|
| **Multi-source Data Ingestion** | Evidence upload works for files | Need parsers for CDRs (CSV), financial transactions (CSV/JSON), FIR/police reports (text/PDF) | Implement CSV parsers for CDRs/financial tx, reuse existing text/PDF handling |
| **Entity Extraction** | Rule-based regex (persons, phones, vehicles, locations, orgs) | LLM-based structured extraction handling aliases/variations, persisted to DB | LLM extraction (person/phone/vehicle/location/org) + fallback spaCy, persist to `intel.entities` |
| **Relationship Mapping** | Proximity-heuristic only, not persisted | Persisted relationships with source traceability, confidence scores | LLM-derived relationship triples (subject-predicate-object) persisted to `intel.entity_relationships` |
| **Key Influencer Identification** | None | Real graph algorithms: centrality, PageRank, community detection | NetworkX integration computing degree/betweenness centrality, PageRank, Louvain communities |
| **Suspicious Pattern Detection** | None | Deterministic rules over entity/relationship tables + temporal analysis | Rule engine for: call-transfer-delivery sequences, burner phone usage, temporal spikes, location reuse patterns |
| **Cross-case Intelligence** | None | Shared entity detection across cases with evidence trails | SQL joins finding entities appearing in ≥2 cases, showing evidence trails |
| **Investigator Interface** | Placeholder frontend | Visual graph + timeline + entity panels + NL query box | React Force/Cytoscape graph view, timeline, entity detail panels, 2-3 shaped NL query endpoint |
| **Evidence Provenance & Explainability** | Findings trace to snapshots | Every graph claim traceable to source text/document | Entity/relationship records include `finding_id` → `snapshot_id` → evidence → source text location |
| **Confidence Scoring** | Basic 0.6-0.8 scores in extraction | Multi-dimensional confidence: extraction, resolution, relationship, source reliability | Confidence model combining extraction confidence, entity-resolution confidence, corroborating evidence count |

## C. Proposed Architecture

### Data Flow
```
Evidence Upload
        → OCR Stage (text extraction)
        → Metadata Stage (EXIF/GPS/timestamps)
        → Entity Extraction Stage (LLM-based: persons/phones/vehicles/locations/orgs)
        → Relationship Extraction Stage (LLM-based triples)
        → Entity Resolution Stage (alias/variation merging with confidence)
        → Persistence Layer (intel.entities, intel.entity_relationships tables)
        → Graph Analytics Layer (NetworkX: centrality, PageRank, communities)
        → Pattern Detection Layer (temporal rules, anomaly detection)
        → API Layer (/graph, /analysis/influencers, /cross-case, /query)
        → Frontend (Graph visualization, timeline, entity panels, investigator query)
```

### Key Components
1. **Enhanced Pipeline Stages**: Replace regex extraction with LLM-based structured extraction
2. **New Database Tables**: `intel.entities`, `intel.entity_relationships`, `intel.entity_mentions` (FK to findings)
3. **Graph Analytics Service**: NetworkX computations cached per case
4. **Pattern Detection Engine**: Deterministic rules over persisted entity/relationship data
5. **Investigator Query Endpoint**: LLM-to-graph-query translation for 2-3 predefined shapes
6. **Frontend Graph View**: Force-directed visualization with click-to-evidence-trace

## D. Database Design

### New Tables (intel schema)
```sql
CREATE TABLE intel.entities (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    entity_type VARCHAR(20) NOT NULL, -- person, phone, vehicle, location, organization
    canonical_value TEXT NOT NULL, -- normalized form (e.g., "Rajesh Kumar")
    entity_metadata JSONB, -- aliases, phones, addresses, etc. specific to type
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(case_id, entity_type, canonical_value)
);

CREATE TABLE intel.entity_relationships (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    subject_entity_id UUID NOT NULL REFERENCES intel.entities(id),
    predicate VARCHAR(50) NOT NULL, -- calls, lives_at, owns, transfers_money_to, etc.
    object_entity_id UUID NOT NULL REFERENCES intel.entities(id),
    confidence_score FLOAT NOT NULL, -- 0.0-1.0
    evidence_json JSONB, -- array of {finding_id, source_text, confidence}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE intel.entity_mentions (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    entity_id UUID NOT NULL REFERENCES intel.entities(id),
    finding_id UUID NOT NULL REFERENCES intel.findings(id),
    source_text TEXT NOT NULL, -- exact text where entity was mentioned
    confidence_score FLOAT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_entities_case_type ON intel.entities(case_id, entity_type);
CREATE INDEX idx_relationships_case ON intel.entity_relationships(case_id);
CREATE INDEX idx_mentions_entity ON intel.entity_mentions(entity_id);
CREATE INDEX idx_mentions_finding ON intel.entity_mentions(finding_id);
```

## E. Intelligence Architecture

### 1. Entity Extraction (LLM-Based)
- **Input**: OCR text + metadata context
- **Output**: Structured JSON per entity type with aliases/variations
- **Model**: Function calling with JSON schema (fallback to spaCy NER)
- **Persistence**: Stores to `intel.entities` with `entity_metadata` containing aliases, phones, etc.
- **Traceability**: Each entity gets mentions in `intel.entity_mentions` linked to source findings

### 2. Relationship Extraction (LLM-Based)
- **Input**: OCR text + extracted entities
- **Output**: Relationship triples (subject-predicate-object) with confidence
- **Model**: Function calling for relationship triples
- **Persistence**: Stores to `intel.entity_relationships` with `evidence_json` array
- **Traceability**: Each relationship links to source findings via `evidence_json`

### 3. Entity Resolution
- **Input**: New entity mentions + existing entities
- **Process**: 
  - Exact match on canonical_value
  - Fuzzy matching on aliases/phones/addresses
  - Confidence scoring based on evidence count, source reliability
  - Merge only when confidence > threshold (e.g., 0.8)
- **Output**: Updated entities with merged metadata, new mentions

### 4. Graph Construction & Analytics
- **Input**: Entities + relationships for a case
- **Process**:
  - Build NetworkX graph (nodes=entities, edges=relationships weighted by confidence)
  - Compute: degree centrality, betweenness centrality, PageRank
  - Detect communities using Louvain algorithm
  - Identify bridges, hubs, peripheral actors
- **Output**: Ranked influencers with graph-theoretic explanations

### 5. Pattern Detection Engine
- **Rules over entity/relationship data**:
  - Temporal spikes: sudden increase in communication frequency
  - Call-transfer-delivery sequences: P1→P2 call → money transfer → physical delivery
  - Burner phone usage: short calls to disposable numbers before activities
  - Location reuse: consistent time windows at specific locations
  - Cash deposit patterns: regular cash after large NEFT
  - Social media correlation: posts correlating with financial transfers
- **Output**: Flagged suspicious patterns with evidence trails

### 6. Cross-case Intelligence
- **Query**: Find entities (person/phone/vehicle) appearing in ≥2 cases
- **Output**: Shared entities with evidence trails from each case
- **Analysis**: Determine connection strength (direct/indirect/weak) based on evidence quality

### 7. Investigator Natural Language Query
- **Supported Shapes** (scoped for demo):
  - "Who connects [Person A] and [Person B]?"
  - "Who is the most central person in this case?"
  - "Show me the financial network of [Person]"
  - "What relationships occurred before [timestamp]?"
- **Process**: LLM translates NL to graph query (Cypher-like) executed over NetworkX
- **Output**: Subgraph + explanation + evidence trails

## F. Evidence/Provenance Architecture

**Every graph claim must be traceable:**
```
Graph Node/Edge
    → intel.entity or intel.entity_relationship record
    → intel.entity_mention(s) or evidence_json array
    → intel.finding record
    → intel.analysis_snapshot record
    → intel.evidence record (source document)
    → OCR text or metadata (exact location where possible)
    → SHA256 hash of evidence file
```

**Implementation**:
- Entity records store `entity_metadata` including source finding IDs
- Relationship records store `evidence_json` array of `{finding_id, source_text, confidence}`
- Entity-mention table provides many-to-many link between entities and findings
- All findings already trace to snapshots → evidence (existing functionality)
- Frontend click-on-node/edge shows source evidence excerpt with highlighting

## G. Confidence Architecture

### Three-Dimensional Confidence Model
1. **Extraction Confidence** (0.0-1.0):
   - Based on LLM output certainty or regex match quality
   - Calibrated against ground truth during development

2. **Entity-Resolution Confidence** (0.0-1.0):
   - Based on number/quality of corroborating evidence pieces
   - Alias match: +0.3, Phone match: +0.4, Address match: +0.3
   - Diminishing returns for additional evidence
   - Threshold for merge: ≥0.8

3. **Relationship Confidence** (0.0-1.0):
   - Based on LLM extraction confidence
   - Adjusted by source reliability (official doc > social media > rumor)
   - Corroboration boost: multiple independent sources increase confidence

### Display Strategy
- **Nodes**: Color intensity = entity-resolution confidence
- **Edges**: Line thickness = relationship confidence, style = solid/dashed based on corroboration
- **Tooltips**: Show extraction/resolution/relationship confidence breakdown
- **Influencer Ranking**: Primary sort = betweenness centrality, secondary = entity-resolution confidence
- **Pattern Flags**: Confidence = min(evidence confidences) × corroboration factor

## H. Feature Priority

### MUST HAVE (Core Intelligence Layer)
1. LLM-based entity extraction (persons, phones, vehicles, locations, organizations) with persistence
2. LLM-based relationship extraction (triples) with persistence and evidence traceability
3. Entity resolution with confidence-scored merging of aliases/variations
4. Knowledge graph tables: `intel.entities`, `intel.entity_relationships`, `intel.entity_mentions`
5. NetworkX graph analytics: degree/betweenness centrality, PageRank, community detection
6. `/api/v1/cases/{id}/graph` endpoint returning nodes/edges JSON
7. `/api/v1/cases/{id}/analysis/influencers` endpoint with ranked key players + explanations
8. Frontend graph visualization (React Force/Cytoscape) with click-to-evidence-trace
9. Deterministic pattern detection engine for call-transfer-delivery, burner phones, temporal spikes
10. Cross-case shared entity detection via SQL joins
11. Investigator NL query endpoint for 2-3 predefined shapes ("who connects X and Y?", "most central")
12. Full provenance traceability from graph claims to source evidence

### SHOULD HAVE (Enhances Credibility & Demo Impact)
1. Temporal relationship timestamps (extract dates/times from text where possible)
2. Uncertainty visualization in graph (dashed lines for low-confidence edges)
3. Entity detail panel showing all aliases, phones, addresses, source evidence
4. Timeline view of events extracted from evidence
5. Simple contradiction detector (same phone used by two "different" people at overlapping times)
6. Evidence confidence scoring based on source type (FIR > CDR > social media > witness statement)
7. Export graph as JSON/CSV for external analysis
8. Basic authentication layer (placeholder for future RBAC)

### WOW FEATURES (High Judge Impact if Time Permits)
1. Real-time streaming simulation (show graph building as evidence processes)
2. "Show me similar patterns" button finding entities with similar connection profiles
3. Anomaly detection highlighting: impossible travel times, sudden relationship formation
4. Cross-case temporal alignment showing correlated activities across cases
5. Voice-to-query investigator interface (push-to-talk microphone in UI)
6. Model confidence calibration showing precision/recall against ground truth

### POST-HACKATHON (1-2 Year Evolution)
1. Millions of records: partitioned tables, async workers, message queue (Redis/RabbitMQ)
2. Streaming data: Kafka consumers for live CDR/financial feeds
3. Temporal knowledge graphs: edges with valid-time intervals, temporal queries
4. Advanced entity resolution: ML-based embedding similarity + rule-based constraints
5. OSINT ingestion: web scraping, social media APIs, dark web monitoring
6. Financial analysis: flow detection, shell company detection, Benford's law
7. Call Detail Record (CDR) analysis: cell tower triangulation, frequent contact detection
8. Multilingual NLP: Hindi/regional language support for Indian law enforcement context
9. Secure/offline deployment: air-gapped variant with local LLM models
10. Model evaluation framework: A/B testing different LLMs, continuous retraining

## I. 1-2 Week Implementation Plan

### Week 1: Backend Foundation (Claude Code)
**Day 1-2: Database & Migration**
- Create Alembic migration for `intel.entities`, `intel.entity_relationships`, `intel.entity_mentions`
- Update SQLAlchemy models.py with new table definitions
- Add repository layer for new entities (EntityRepository, RelationshipRepository)
- Write unit tests for new models and repositories

**Day 3-4: LLM Entity Extraction**
- Replace `entity_extraction.py` rule-based regex with LLM-based structured extraction
- Implement function calling with JSON schema for person/phone/vehicle/location/organization
- Persist extracted entities to `intel.entities` with metadata (aliases, phones, etc.)
- Create entity mentions linking to source findings
- Add fallback to spaCy NER for low-latency scenarios
- Unit test with sample texts from demo dataset

**Day 5: LLM Relationship Extraction**
- Build relationship extraction stage producing subject-predicate-object triples
- Persist to `intel.entity_relationships` with evidence_json array
- Link relationships to source findings via evidence_json
- Unit test with co-occurrence patterns from demo dataset

**Day 6: Entity Resolution Service**
- Implement resolution service that merges aliases/variations
- Confidence scoring based on evidence count and source reliability
- Update existing entities or create new resolved entities
- Handle merge conflicts with manual review flag (for future)
- Test resolution accuracy against demo dataset ground truth

**Day 7: Graph Analytics & API Endpoints**
- Integrate NetworkX for centrality (degree/betweenness), PageRank, Louvain communities
- Build `/graph` endpoint: nodes + edges JSON with confidences and metadata
- Build `/analysis/influencers` endpoint: ranked list with graph-theoretic explanations
- Add caching layer for expensive graph computations
- Integration test: full pipeline on single evidence → graph output

### Week 2: Features, Frontend & Validation (Claude Code + Hermes)
**Day 8-9: Pattern Detection & Cross-case Intelligence**
- Implement deterministic pattern detector:
  - Call-transfer-delivery sequences
  - Burner phone usage (<60s calls to disposables before activity)
  - Temporal spikes in communication frequency
  - Location reuse at specific time windows
  - Cash deposit patterns post-large NEFT
- Build `/cross-case` endpoint: shared entities (≥2 cases) with evidence trails
- Test pattern detection accuracy against demo dataset ground truth

**Day 10-11: Frontend Development**
- Case list/detail wired to real API (exists, needs UI)
- Evidence upload/list wired to real API
- Knowledge graph view: Force-directed visualization (React Force/Cytoscape)
  - Node color by entity type, size by centrality
  - Click node → side panel: entity details, aliases, source evidence with highlighting
  - Click edge → relationship details, confidence, source evidence
- Influencer panel: ranked list with explanations from `/analysis/influencers`
- Timeline view: extract dates/times from evidence, show events chronologically
- Investigator query box: 2-3 predefined NL shapes → API → subgraph visualization

**Day 12: Investigator NL Query Endpoint**
- Implement LLM-to-graph-query translation for:
  - "Who connects [Person A] and [Person B]?" → shortest path query
  - "Who is the most central person in this case?" → betweenness centrality ranking
  - "Show me the financial network of [Person]" → subgraph of money-transfer relationships
- Return subgraph JSON + natural language explanation + evidence trails
- Frontend integration: query box → API → highlighted subgraph in visualization

**Day 13: Validation Against Ground Truth**
- Build validation script (Hermes responsibility) running full pipeline on `demo_data_v2`
- Compare extracted entities/relationships against `CANONICAL_ENTITIES_AND_RELATIONSHIPS.json`
- Calculate precision/recall by entity type and relationship predicate
- Test entity resolution accuracy (merging aliases correctly)
- Verify pattern detection flags match ground truth suspicious patterns
- Generate validation report with metrics for demo

**Day 14: Demo Preparation & Rehearsal**
- End-to-end Docker Compose smoke test daily
- Rehearse demo script: upload evidence → watch graph build → click influencer → trace evidence → ask NL query
- Stress test with red herring entities: verify system doesn't over-weight false positives
- Prepare talking points emphasizing explainability: "every claim traces back to evidence"
- Finalize presentation materials and talking points

## J. Testing/Evaluation Plan

### Unit & Integration Testing
- Test new pipeline stages in isolation with mock LLM responses
- Test database repositories with factory-boy style test data
- Test graph analytics with known graph fixtures
- Test pattern detector with synthetic evidence sequences
- Test NL query endpoint with predefined question/answer pairs

### Ground Truth Validation (Hermes Lead)
- **Entity Extraction Precision/Recal**: By type (person, phone, vehicle, location, org)
- **Relationship Extraction Precision/Recall**: By predicate type (calls, lives_at, transfers_money_to, etc.)
- **Entity Resolution Accuracy**: Percentage of aliases correctly merged vs false merges
- **Pattern Detection Accuracy**: % of ground truth suspicious patterns correctly flagged
- **Cross-case Detection**: Accuracy of shared entity identification between cases
- **End-to-end Pipeline Latency**: Time from evidence upload to graph visualization ready

### Adversarial Testing (Hermes Lead)
- **Red herring resistance**: Ensure system doesn't inflate scores for legitimate look-alikes
- **Noise injection**: Add irrelevant text, verify doesn't create false relationships
- **Confounding entities**: Test with multiple people sharing names, verify resolution uses phones/addresses
- **Temporal confounding**: Test impossible timelines don't create false causal relationships
- **Source reliability**: Verify official documents weighted higher than social media rumors

### Performance Testing
- Baseline latency: single evidence processing (<5s target)
- Batch processing: 10 evidences concurrently (<30s target)
- Memory usage: NetworkX graph computation footprint
- API response time: /graph endpoint (<2s for medium case)

### Metrics for Demo
Hermes will generate a validation report showing:
- "Entity extraction accuracy: 92% precision, 88% recall against hand-labeled ground truth"
- "Relationship extraction accuracy: 85% precision, 80% recall"
- "Entity resolution correctly merged 95% of aliases with <2% false merges"
- "Detected 8/10 ground truth suspicious patterns with 0 false positives on legitimate activity"
- "Cross-case connection identified shared entities with correct evidence trails"
- "Average pipeline latency: 3.2s per evidence item"

## K. Demo Plan (5-8 Minute Story)

**Narrative**: "From Fragmented Evidence to Actionable Intelligence"

### Setup (30 seconds)
- Show BlackBox dashboard: "AI-Powered Criminal Network Analysis System"
- Explain the problem: "Investigators have evidence scattered across FIRs, CDRs, financial reports, surveillance..."
- Load demo case: "Case 001: Missing person investigation with suspected drug trafficking"

### Evidence Ingestion & Processing (60 seconds)
- Upload multiple evidence types:
  1. FIR PDF (missing person report)
  2. CDR CSV (call logs showing frequent contacts)
  3. Financial transaction CSV (bank transfers)
  4. Surveillance report text (observations at VIP Road)
  5. Social media screenshot (Facebook/WhatsApp extracts)
- Show pipeline stages executing: OCR → Metadata → Entity Extraction → Relationship Extraction → Resolution → Graph Analytics
- Display real-time status: "Extracting entities... Building graph... Computing centrality..."

### Graph Emergence & Key Insights (90 seconds)
- Reveal force-directed graph with nodes/edges appearing
- Highlight visualization features:
  - Node colors: persons (blue), phones (green), vehicles (orange), locations (purple), orgs (red)
  - Node size: centrality (larger = more important)
  - Edge thickness: relationship confidence
  - Dashed edges: lower confidence relationships
- Click on high-centrality node (Priya Sharma):
  - Side panel shows: name, aliases ["Priya"], phone, associated organizations [Shyam Traders]
  - Source evidence: "Appears in FIR_001 as complainant, financial records show directorship"
  - Connections shown: Rajesh Kumar (supplier), Vikram Singh (courier), financial accounts, residences
- Explain: "Priya Sharma emerges as central financial/logistics hub - not the supplier or courier, but the connector"

### Pattern Detection & Alerts (60 seconds)
- Show pattern detection panel lighting up:
  - 🔴 "Call-transfer-delivery sequence detected": Rajesh→Priya call → money transfer → Vikram delivery
  - 🔴 "Temporal spike": 200% increase in Priya-Rajesh calls before financial transfers
  - 🔴 "Location reuse": L003 used repeatedly at 23:50-00:30 for exchanges
  - 🔴 "Burner phone": Vikram uses disposable PH021 for short calls before deliveries
- Click each pattern to see: evidence trail, timing analysis, confidence score

### Cross-case Investigation & NL Query (60 seconds)
- Switch to Case 002: "Separate money laundering investigation"
- Show graph for Case 2: Sameer Khan (money launderer) network
- Click "Cross-case connections" button:
  - System highlights: Officer Pooja Sharma (P005) appears in both cases
  - Evidence trail: "Consulted on Case 2 by Financial Intelligence Officer (P007)"
  - Explanation: "Official information sharing between investigating officers"
- Demonstrate investigator NL query:
  - User types: "Who connects the drug supplier in Case 1 and the money launderer in Case 2?"
  - System processes: LLM translates to graph query → finds path: Rajesh Kumar → Priya Sharma → Pooja Sharma → Deepak Mehta → Sameer Khan
  - Returns: subgraph visualization + explanation: "Connection via investigating officer consultation"
  - Shows evidence trail: FIRs, officer exchange records, intelligence sharing logs

### Closing & Impact (30 seconds)
- Return to Case 1 graph, click on Rajesh Kumar (supplier):
  - Trace: Rajesh Kumar → (call log evidence) → Priya Sharma → (financial record) → Shyam Traders → (surveillance) → L003 → (delivery evidence) → Vikram Singh
- Emphasize: "Every connection traces back to source evidence - no black box inferences"
- Final message: "BlackBox doesn't replace investigators - it gives them superhuman connectivity vision"
- Show validation metrics: "92% entity extraction accuracy against adversarial ground truth with red herrings"

## L. Long-Term Architecture (1-2 Year Vision)

### Scalability Foundation
- **Async Processing Pipeline**: Evidence upload → message queue (Redis) → worker pool → result storage
- **Partitioned Tables**: `intel.entities_partitioned` by case_id range for millions of records
- **Read Replicas**: Graph analytics queries on replicas to avoid impacting transactional DB
- **Caching Layer**: Redis cache for frequently accessed graphs, centrality scores, pattern results

### Temporal Knowledge Graph
- **Temporal Edges**: Relationships with `valid_from`/`valid_to` timestamps extracted from text
- **Temporal Queries**: "Show me relationships active between Jan 10-20, 2026"
- **Event Detection**: Alert on relationship formation/dissolution anomalies
- **Temporal Centrality**: Measures that account for edge validity periods

### Advanced Entity Resolution
- **Embedding-based Similarity**: Sentence Transformers for name/address similarity scoring
- **Constraint Programming**: Hard constraints (same phone = same person unless burner evidence)
- **Confidence Propagation**: Resolution confidence affects relationship confidence calculations
- **Manual Review Queue**: Low-confidence merges flagged for investigator review

### Multimodal & OSINT Expansion
- **OCR Expansion**: Handwritten text, layout-aware extraction (PDF forms/tables)
- **Speech-to-Text**: CDR audio transcripts, surveillance audio, witness interviews
- **OSINT Ingestors**: Social media APIs, news scrapers, public records, dark web monitors
- **Image Analysis**: Face detection in surveillance, object detection (weapons, vehicles), scene classification
- **Geospatial Analysis**: Hotspot detection, route reconstruction, geofencing alerts

### Specialized Analytical Modules
- **Financial Crimes**: Shell company detection, money laundering layering, trade-based laundering
- **Cyber Crimes**: IP address clustering, malware hash correlation, dark web marketplace monitoring
- **Human Trafficking**: Hotel record correlation, travel document analysis, online advertisement scraping
- **Counterfeit Goods**: Supply chain tracing, marketplace monitoring, authentication verification

### Enterprise Features
- **Role-Based Access Control**: Case-based permissions, data classification levels
- **Audit Trail**: Immutable append-only logs of all graph queries and exports
- **Encryption**: At-rest (Transparent Data Encryption) and in-transit (TLS 1.3)
- **Model Management**: LLM registry, A/B testing framework, continuous retraining pipeline
- **Deployment Options**: Kubernetes Helm charts, air-gapped variant, cloud-agnostic Terraform

## M. Top Technical Risks

### Risk 1: LLM Latency/Cost Overrun (Probability: Medium, Impact: High)
- **Mitigation**: 
  - Implement spaCy NER fallback for low-latency paths
  - Cache LLM responses for repeated extractions
  - Use batch processing for multiple evidences
  - Set strict timeout limits with graceful degradation
  - Monitor token usage during development

### Risk 2: Entity Resolution False Merges (Probability: Medium, Impact: Critical)
- **Mitigation**:
  - Require multiple corroborating evidence pieces for merge (phone + address OR 2+ aliases)
  - Implement source reliability weighting (official > social media)
  - Provide manual review queue for low-confidence merges
  - Validate extensively against demo dataset ground truth with red herrings
  - Never auto-merge on name similarity alone

### Risk 3: Graph Visualization Performance (Probability: Low, Impact: Medium)
- **Mitigation**:
  - Limit graph size to top 50 nodes by centrality for initial load
  - Implement progressive disclosure: load more nodes on demand
  - Use canvas-based rendering (not SVG) for large graphs
  - WebWorker offload for layout calculations
  - Level-of-detail rendering: simplify distant nodes

### Risk 4: False Confidence in AI Outputs (Probability: Medium, Impact: High)
- **Mitigation**:
  - Never present inference as fact - always show confidence and evidence
  - UI pattern: "System suggests [X] with [Y]% confidence based on [evidence]"
  - Require investigator confirmation for critical actions
  - Extensive ground truth validation to calibrate confidence scores
  - Pattern detection shows raw evidence, not just alerts

### Risk 5: Scope Creep on Nice-to-haves (Probability: High, Impact: Medium)
- **Mitigation**:
  - Strict adherence to MUST HAVE list for Week 1-2
  - Hermes owns validation and will block non-essential features
  - Daily check-ins: "Is this critical for demo or just nice to have?"
  - WOW features only attempted if all MUST HAVE are complete and tested
  - Demo rehearsal focuses on core flow, not edge cases

## N. Critical Decisions Needing Your Approval

Before implementation begins, I need your explicit approval on:

### 1. LLM Integration Strategy
- **Option A**: Primary LLM extraction with spaCy fallback (Recommended)
- **Option B**: Pure regex extraction with post-hoc LLM resolution (Lower risk, less capable)
- **Option C**: Pure LLM extraction no fallback (Highest capability, highest risk)
*Recommendation: Option A - gives us best capability with safety net*

### 2. Graph Technology Choice
- **Option A**: NetworkX (pure Python, zero infra, fast enough for <10k nodes) (Recommended)
- **Option B**: Neo4j Aura cloud graph database (separate service, more complex)
- **Option C**: Amazon Neptune or similar managed graph service
*Recommendation: Option A - keeps it simple, demo-ready, no external deps*

### 3. Investigator NL Query Scope
- **Option A**: 2-3 predefined shapes only (who connects X/Y, most central, financial network) (Recommended)
- **Option B**: Open-ended NL-to-Cypher translation (ambitious but risky for demo)
- **Option C**: Keyword-based query interface (limited but safe)
*Recommendation: Option A - delivers wow factor with controlled risk*

### 4. Pattern Detection Approach
- **Option A**: Deterministic rules over entity/relationship tables (Recommended)
- **Option B**: ML anomaly isolation forests/one-class SVMs (requires training data)
- **Option C**: Hybrid: rules + simple statistical outliers
*Recommendation: Option A - explainable, demoable, validated against ground truth*

### 5. Frontend Graph Library
- **Option A**: React Force Graph (WebGL-based, good performance, MIT licensed) (Recommended)
- **Option B**: Cytoscape.js (feature-rich but heavier)
- **Option C**: vis.js Network (simpler but less customizable)
- **Option D**: D3.js force layout (maximum control, most code)
*Recommendation: Option A - best balance of performance, features, and ease of use*

### 6. Validation Rigor Level
- **Option A**: Precision/recall against demo dataset ground truth (Recommended)
- **Option B**: + adversarial testing with crafted edge cases
- **Option C**: + cross-validated temporal splitting (not applicable here)
- **Option D**: + human law enforcement reviewer (not feasible in timeline)
*Recommendation: Option A+B - gives us credible metrics to share with judges*

Please provide your decisions on these 6 critical points, and I will begin implementation immediately following your approval.