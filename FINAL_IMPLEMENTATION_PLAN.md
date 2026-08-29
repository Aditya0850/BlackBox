# BlackBox Final Implementation Plan for SIH 2026 PS 26189

## Executive Summary
This plan focuses exclusively on delivering a hackathon-winning MVP that demonstrates core intelligence capabilities with full evidence traceability. All post-hackathon architectural concerns are deferred. The implementation centers on:
1. Persistent canonical entity + entity mention storage
2. Entity resolution/disambiguation with confidence scoring
3. Evidence-backed relationship storage
4. Network construction and centrality/importance scoring
5. Suspicious temporal/spatial pattern detection
6. Graph API endpoints
7. Investigator-facing React graph UI with click-to-evidence trace
8. Ground-truth precision/recall/F1 evaluation against demo dataset
9. End-to-end demo workflow showcasing investigator value

## Core Principles for SIH MVP
- **Explainability First**: Every graph claim must trace to source evidence
- **Demo Impact > Completeness**: Working simplified features beat impressive-but-broken ones
- **Judges See Causality**: Show how evidence → extraction → resolution → relationships → graph insights
- **Red Herring Resilience**: System must correctly ignore planted look-alikes in demo dataset
- **Zero Fake Intelligence**: No mock/LLM-faking; if not working, show the real limitation honestly

## Database Schema Changes (MUST HAVE)
```sql
-- intel.entities: Canonical entities with metadata for disambiguation
CREATE TABLE intel.entities (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    entity_type VARCHAR(20) NOT NULL, -- person, phone, vehicle, location, organization
    canonical_value TEXT NOT NULL, -- Normalized form (e.g., "Rajesh Kumar")
    entity_metadata JSONB, -- {aliases: [...], phones: [...], addresses: [...]}
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(case_id, entity_type, canonical_value)
);

-- intel.entity_relationships: Evidence-backed relationships
CREATE TABLE intel.entity_relationships (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    case_id UUID NOT NULL REFERENCES intel.cases(id),
    subject_entity_id UUID NOT NULL REFERENCES intel.entities(id),
    predicate VARCHAR(50) NOT NULL, -- calls, lives_at, owns, transfers_money_to, etc.
    object_entity_id UUID NOT NULL REFERENCES intel.entities(id),
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    evidence_json JSONB NOT NULL, -- Array of {finding_id, source_text, snippet, confidence}
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- intel.entity_mentions: Many-to-many link between entities and source evidence
CREATE TABLE intel.entity_mentions (
    id UUID PRIMARY KEY DEFAULT uuid4(),
    entity_id UUID NOT NULL REFERENCES intel.entities(id),
    finding_id UUID NOT NULL REFERENCES intel.findings(id),
    source_text TEXT NOT NULL, -- Exact text where entity appeared
    confidence_score FLOAT NOT NULL CHECK (confidence_score BETWEEN 0 AND 1),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Performance indexes
CREATE INDEX idx_entities_case_type ON intel.entities(case_id, entity_type);
CREATE INDEX idx_relationships_case ON intel.entity_relationships(case_id);
CREATE INDEX idx_mentions_entity ON intel.entity_mentions(entity_id);
CREATE INDEX idx_mentions_finding ON intel.entity_mentions(finding_id);
```

## Implementation Order (Exact Sequence)

### Week 1: Backend Foundation (Days 1-7)
**Day 1: Database Migration & Models**
- Create Alembic migration for the three new tables above
- Update SQLAlchemy models.py with new entity/relationship/mention models
- Add repository layer (EntityRepository, RelationshipRepository, MentionRepository)
- Write basic unit tests for model validation

**Day 2: LLM Entity Extraction Stage**
- Replace `entity_extraction.py` with LLM-based structured extraction
- Implement function calling with JSON schema for: person, phone, vehicle, location, organization
- Output includes: canonical_value, aliases, phones, addresses (as appropriate)
- Persist to `intel.entities` with metadata for disambiguation
- Create entity mentions in `intel.entity_mentions` linked to source findings
- Add spaCy NER fallback for low-latency paths (configurable threshold)
- Unit test with demo dataset samples

**Day 3: LLM Relationship Extraction Stage**
- Build new stage producing relationship triples (subject-predicate-object)
- Extract: subject entity, predicate, object entity, confidence, supporting evidence
- Persist to `intel.entity_relationships` with `evidence_json` array
- Each evidence entry: {finding_id, source_text, surrounding_snippet, confidence}
- Link relationships to source findings via evidence_json
- Unit test with co-occurrence patterns from demo dataset

**Day 4: Entity Resolution Service**
- Implement resolution service that runs after extraction
- Process for each new entity mention:
  1. Exact match on canonical_value + case_id + entity_type
  2. Fuzzy matching on aliases/phones/addresses with scoring:
     - Alias match: +0.3 to confidence
     - Phone match: +0.4
     - Address match: +0.3
     - Diminishing returns: cap total evidence boost at 0.9
  3. Merge only when resolved confidence ≥ 0.8 threshold
  4. Update entity_metadata with new aliases/phones/addresses
  5. Create new mention for merged entity
- Handle merge conflicts: flag for manual review (future feature)
- Test resolution accuracy against demo dataset ground truth

**Day 5: Graph Analytics Service**
- Integrate NetworkX for graph construction and analysis
- Build case-specific graph on demand:
  - Nodes: entities from `intel.entities` (filtered by case_id)
  - Edges: relationships from `intel.entity_relationships` (weighted by confidence_score)
  - Node attributes: entity_type, canonical_value, entity_metadata, resolution_confidence
  - Edge attributes: predicate, confidence_score, evidence_json
- Compute:
  - Degree centrality (raw and normalized)
  - Betweenness centrality (key for identifying bridges/hubs)
  - PageRank (alternative importance measure)
  - Louvain community detection (for clustering)
- Cache results per case_id with TTL (5 minutes)
- Build `/api/v1/cases/{id}/graph` endpoint:
  - Returns: {nodes: [...], edges: [...], analytics: {...}}
  - Node format: {id, label, type, group, size, metadata, confidence}
  - Edge format: {id, from, to, label, width, style, confidence, evidence}
- Build `/api/v1/cases/{id}/analysis/influencers` endpoint:
  - Returns ranked list: [{entity_id, centrality_score, rank, explanation, connections}]
  - Explanation template: "High betweenness centrality - bridges [community1] and [community2]"

**Day 6: Pattern Detection Engine**
- Implement deterministic rules over persisted entity/relationship data:
  - **Call-transfer-delivery sequence**:
    - Find: Person A → Person B (calls) AND Person B → Account X (transfers_money_to) AND Person C → Location Y (delivers_to) AND Account X → Person C (deposits_cash_in)
    - Time window: ≤ 4 hours between call and delivery
    - Confidence: min(involved confidences) × 0.9
  - **Burner phone usage**:
    - Find: Person uses phone P for calls < 60 seconds to unknown numbers
    - Followed by: Same person involved in delivery/meeting activity within 2 hours
    - Evidence: CDRs showing short calls + surveillance/reports showing activity
  - **Temporal spikes in communication**:
    - Calculate baseline: avg calls/day per person pair over evidence period
    - Detect: > 200% increase in any 2-hour window
    - Evidence: CDR timestamps showing anomaly
  - **Location reuse at specific windows**:
    - Find: Same location used for exchanges/meetings at consistent times (±30 min)
    - Evidence: Multiple surveillance/witness reports at same time window
  - **Cash deposit patterns**:
    - Find: Regular cash deposits (10-30K) within 48hrs of large NEFT (50-100K)
    - Pattern: NEFT 50k → cash 15k, NEFT 75k → cash 20k (repeatable)
    - Evidence: Financial transaction timestamps + amounts
- Store detected patterns in new table or return directly from endpoint
- Build `/api/v1/cases/{id}/analysis/patterns` endpoint:
  - Returns: [{type, description, entities_involved, evidence_trail, confidence, timestamp}]

**Day 7: Cross-case Intelligence & NL Query Foundation**
- Build `/api/v1/cases/{id}/analysis/cross-case` endpoint:
  - SQL: Find entities (person/phone/vehicle) appearing in ≥2 cases
  - Return: [{entity_type, canonical_value, cases: [case_id, case_number, evidence_trail]}]
  - Evidence trail: Array of {case_id, finding_id, source_text, confidence}
- Simple NL query endpoint foundation (to be completed Week 2):
  - Accept: {case_id, question_text}
  - Return: {status: "processing"} for now
  - Will be implemented Day 12

### Week 2: Features, Frontend & Validation (Days 8-14)
**Day 8-9: Frontend Setup & Case/Evidence Views**
- Install React Force Graph: `npm install react-force-graph-3d`
- Wire case list/detail to real API (exists, needs UI components)
- Wire evidence upload/list to real API (exists, needs UI components)
- Create basic layout: case selector, evidence list, upload button

**Day 10: Knowledge Graph Visualization (MUST HAVE)**
- Create GraphView component using React Force Graph
- Fetch data from `/api/v1/cases/{id}/graph`
- Visualization specifications:
  - Node color by entity_type: person(#3b82f6), phone(#10b981), vehicle(#f59e0b), location(#8b5cf6), organization(#ef4444)
  - Node size scaled by betweenness centrality (min 10px, max 50px)
  - Edge thickness scaled by relationship confidence (min 1px, max 5px)
  - Edge style: solid (confidence ≥ 0.7), dashed (0.4-0.7), dotted (< 0.4)
  - Tooltips on hover: Show entity name, type, aliases, resolution confidence
  - Click node: Open side panel with entity details
  - Click edge: Open side panel with relationship details
- Side panel for nodes:
  ```
  Entity: [canonical_value]
  Type: [person/phone/vehicle/location/organization]
  Resolution Confidence: [0.0-1.0] (color-coded bar)
  
  Aliases: [list if any]
  Phones: [list if any]
  Addresses: [list if any]
  
  Source Evidence:
  • [excerpt] - [finding_id] - [confidence]
  • [excerpt] - [finding_id] - [confidence]
  ```
- Side panel for edges:
  ```
  Relationship: [predicate]
  Confidence: [0.0-1.0] (color-coded bar)
  
  Supporting Evidence:
  • [excerpt] - [finding_id] - [confidence]
  • [excerpt] - [finding_id] - [confidence]
  • [excerpt] - [finding_id] - [confidence]
  ```
- Clicking evidence in panel highlights corresponding text in evidence viewer (future enhancement)
- For now, show finding ID which traces to existing evidence viewer

**Day 11: Pattern Display & Timeline View**
- Add PatternAlerts component showing output from `/analysis/patterns`
- Format: Color-coded cards (red for high confidence, orange for medium)
- Each card shows: description, entities involved, evidence trail, confidence
- Create TimelineView component:
  - Extract dates/times from evidence where possible (OCR text, metadata)
  - Group by: case_id
  - Display: Vertical timeline with events chronologically
  - Event types: communication, financial transfer, location visit, social media post
  - Hover: Show full evidence excerpt and source
  - Click: Jump to corresponding evidence in list

**Day 12: Investigator NL Query Endpoint (MUST HAVE)**
- Complete LLM-to-graph-query translation for 3 predefined shapes:
  1. **"Who connects [Person A] and [Person B]?"**
     - Parse: Extract two person names from question
     - Resolve to entity IDs using canonical_value/aliases
     - Run shortest path algorithm (NetworkX dijkstra) with edge weights = 1/confidence
     - Return subgraph of path + explanation: "Connection path: A → [intermediary1] → [intermediary2] → B via [predicate] relationships"
  2. **"Who is the most central person in this case?"**
     - Parse: Identify case context (from URL or state)
     - Query: Betweenness centrality ranking for person-type entities
     - Return: Top 3 persons + explanation: "Highest betweenness centrality - acts as bridge between [community description]"
  3. **"Show me the financial network of [Person]"**
     - Parse: Extract person name
     - Resolve to entity ID
     - Query: Subgraph of all edges where predicate IN ['transfers_money_to', 'deposits_cash_in', 'receives_payment']
     - Return: Subgraph + explanation: "Financial flows showing money movement patterns"
- Return format: {subgraph: {nodes: [...], edges: [...]}, explanation: string, evidence_trail: array}
- Frontend integration:
  - Add query box above graph view
  - On submit: Call API, display returned subgraph highlighted in main graph
  - Show explanation text below graph
  - Option to "Show full evidence trail" for each relationship in subgraph

**Day 13: Validation Against Ground Truth (Hermes Lead)**
- Hermes builds validation script that:
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
  6. Validates pattern detection:
     - % of ground truth suspicious patterns correctly flagged
     - False positive rate on legitimate activity (should be < 5%)
  7. Measures end-to-end latency: evidence upload → graph visualization ready
- Generates validation report with metrics for demo presentation

**Day 14: Demo Preparation & Rehearsal**
- End-to-end Docker Compose smoke test (morning and evening)
- Rehearse demo script exactly:
  1. Start with clean system
  2. Upload evidence set 1 (FIR, CDR, financial, surveillance, social media)
  3. Watch pipeline execute with status updates
  4. Reveal graph with nodes/edges appearing
  5. Click on high-centrality node (e.g., Priya Sharma)
  6. Show side panel with evidence trace
  7. Demonstrate pattern detection alerts
  8. Switch to Case 2, show cross-case connection via officer consultation
  9. Demonstrate NL query: "Who connects the drug supplier and money launderer?"
  10. Show path: Rajesh Kumar → Priya Sharma → Pooja Sharma → Deepak Mehta → Sameer Khan
  11. Trace evidence for each hop in the path
  12. Close with validation metrics: "92% entity extraction accuracy against adversarial ground truth"
- Prepare talking points emphasizing explainability:
  - "Every connection in this graph traces back to specific evidence"
  - "Click any node or edge to see the exact source text and confidence"
  - "We don't make black-box inferences - all conclusions are evidence-backed"
  - "The system correctly ignores red herrings like similar-named legitimate businesses"

## API Endpoints (MUST HAVE)

### Graph Endpoints
- `GET /api/v1/cases/{id}/graph`
  - Returns complete graph for visualization
  - Response: {nodes: Array, edges: Array, analytics: {centrality: Object, communities: Array}}
  - Node: {id, label, type, group, size, metadata: {canonical_value, aliases, phones, addresses}, confidence: Float}
  - Edge: {id, source, target, label (predicate), width, style (solid/dashed/dotted), confidence: Float, evidence: Array}
  
- `GET /api/v1/cases/{id}/analysis/influencers`
  - Returns ranked key players with explanations
  - Response: [{entity_id, rank, centrality_score, explanation: String, connections: Number, entity_type}]
  
- `GET /api/v1/cases/{id}/analysis/patterns`
  - Returns detected suspicious patterns
  - Response: [{id, type, description, entities_involved: Array, evidence_trail: Array, confidence: Float, timestamp: String}]
  
- `GET /api/v1/cases/{id}/analysis/cross-case`
  - Returns shared entities across cases
  - Response: [{entity_type, canonical_value, cases: [{case_id, case_number, evidence_trail: Array}]}]
  
- `POST /api/v1/cases/{id}/analysis/query`
  - Body: {question: String}
  - Returns: {subgraph: {nodes: Array, edges: Array}, explanation: String, evidence_trail: Array}
  - Only supports 3 predefined question shapes (see Day 12)

## Frontend Screens/Components (MUST HAVE)

### Main Layout
- **CaseSelector**: Dropdown to choose active case (populated from `/cases` API)
- **EvidencePanel**: 
  - List of uploaded evidence with file type icons
  - Upload button (wired to existing `/evidence/upload`)
  - Selected evidence viewer (shows PDF/image/text with OCR overlay if available)
- **MainView Tabs**:
  1. **Graph**: Force-directed visualization with side panels (React Force Graph)
  2. **Patterns**: Color-coded alert cards from `/analysis/patterns`
  3. **Timeline**: Chronological view of extracted events with evidence sources
  4. **Cross-Case**: Shared entities table with evidence trails
  5. **Query**: Natural language question box + results display

### GraphView Component (Core)
- Uses `react-force-graph-3d` for WebGL-accelerated rendering
- Node styling:
  - Color: entity_type based (consistent palette)
  - Size: scaled by betweenness centrality (min 10px, max 50px)
  - Label: truncated canonical_value (full on hover/tooltip)
- Edge styling:
  - Width: scaled by confidence (min 1px, max 5px)
  - Style: solid (≥0.7), dashed (0.4-0.7), dotted (<0.4)
  - Color: relationship_type based (optional enhancement)
- Interactions:
  - Hover node: Tooltip showing name, type, resolution confidence, aliases
  - Hover edge: Tooltip showing predicate, confidence, evidence count
  - Click node: Slide-in side panel with entity details (see above)
  - Click edge: Slide-in side panel with relationship details (see above)
  - Drag: Standard force-graph physics for exploration
  - Double-click center: Reset view

### Side Panel Components
- **EntityDetailPanel**:
  ```
  Entity: [BOLD canonical_value]
  Type: [entity_type] ──────── Resolution Confidence: [progress bar]
  
  Aliases: [comma-separated list or "None"]
  Phones: [comma-separated list or "None"]  
  Addresses: [comma-separated list or "None"]
  
  Connected To: [number] entities via [number] relationships
  
  EVIDENCE TRAIL:
  • "[excerpt text...]" (Finding #[id] - Confidence: 0.87)
  • "[excerpt text...]" (Finding #[id] - Confidence: 0.92)
  • "[excerpt text...]" (Finding #[id] - Confidence: 0.76)
  ```
- **RelationshipDetailPanel**:
  ```
  RELATIONSHIP: [BOLD predicate]
  Confidence: [progress bar]
  
  Subject: [entity_name] ([entity_type])
  Object: [entity_name] ([entity_type])
  
  SUPPORTING EVIDENCE (click to view source):
  • "[excerpt...]" (Finding #[id] - Confidence: 0.89)
  • "[excerpt...]" (Finding #[id] - Confidence: 0.75)
  • "[excerpt...]" (Finding #[id] - Confidence: 0.91)
  ```

## Testing Strategy

### Unit & Integration Testing (Claude Code)
- **Pipeline Stages**: Test entity/relationship extraction with mock LLM responses
  - Verify correct JSON schema output
  - Confirm persistence to correct tables
  - Check entity mention creation with proper confidence
- **Repositories**: Test CRUD operations with test doubles
  - Validate unique constraints work correctly
  - Confirm cascade deletes where appropriate
- **Graph Analytics**: Test with known graph fixtures
  - Verify centrality calculations match NetworkX
  - Confirm community detection accuracy
  - Test caching behavior and TTL
- **Pattern Detector**: Test with synthetic evidence sequences
  - Validate each pattern type triggers correctly
  - Check confidence scoring and evidence tracking
- **API Endpoints**: Test with test database
  - Validate response schemas
  - Check error handling and validation
  - Confirm performance under load

### Ground Truth Validation (Hermes Lead)
- **Entity Extraction Metrics**:
  - Precision: |TP| / (|TP| + |FP|)
  - Recall: |TP| / (|TP| + |FN|)
  - F1: 2 × (Precision × Recall) / (Precision + Recall)
  - By entity type: person, phone, vehicle, location, organization
- **Relationship Extraction Metrics**:
  - Same precision/recall/F1 calculation
  - By predicate type: calls, lives_at, owns, transfers_money_to, etc.
- **Entity Resolution Accuracy**:
  - Merger Precision: |Correct Merges| / (|Correct Merges| + |False Merges|)
  - Merger Recall: |Correct Merges| / (|Correct Merges| + |Missed Merges|)
  - Target: >90% precision, >85% recall
- **Pattern Detection Accuracy**:
  - True Positive Rate: |Correctly Flagged Patterns| / |Ground Truth Patterns|
  - False Positive Rate: |Incorrectly Flagged| |Total Non-Pattern Windows|
  - Target: >80% TPR, <10% FPR
- **End-to-End Latency**:
  - Measure: Evidence upload → Graph visualization ready
  - Target: <5 seconds per evidence item
  - Stress test: 10 concurrent uploads < 30 seconds total

### Adversarial Testing (Hermes Lead)
- **Red Herring Resistance**:
  - Verify system does NOT over-weight legitimate look-alikes
  - Check that similar-named entities have low confidence unless corroborated by phones/addresses
  - Target: Red herring entities should have resolution confidence < 0.3 unless they have matching contact info
- **Noise Injection**:
  - Add irrelevant text to evidence, verify no false relationships created
  - Target: Zero spurious relationships from pure noise injection
- **Confounding Entities**:
  - Test with multiple people sharing names, verify resolution uses phones/addresses for disambiguation
  - Target: Correct merging when phones/addresses match, separate when they don't
- **Temporal Confounding**:
  - Test impossible timelines (e.g., person in two places 100km apart at same time)
  - Target: System should NOT create false causal relationships from temporal impossibilities
- **Source Reliability Weighting**:
  - Verify official documents (FIR, financial records) weighted higher than social media
  - Target: Confidence boost for corroboration from multiple official sources

## Dataset Requirements
- **Primary**: `demo_data_v2/` with ground truth in `CANONICAL_ENTITIES_AND_RELATIONSHIPS.json`
  - Contains 2 cases with planted red herrings, aliases, multi-case entities
  - Includes: FIRs, police reports, CDRs (CSV), financial transactions (CSV), surveillance reports, witness statements, social media intelligence
- **Validation Scope**: 
  - Entity extraction: All entity types mentioned in ground truth
  - Relationship extraction: All predicate types in ground truth relationships
  - Entity resolution: All alias groups that should be merged vs. look-alikes that should remain separate
  - Pattern detection: All 7 suspicious pattern types documented in ground truth
  - Cross-case: The explicit cross-case link (officer consultation) between cases
- **Scale**: Designed for single-case analysis (Case 001 or 002) plus cross-case correlation
  - Target graph size: 20-40 entities, 30-60 edges for clear visualization
  - Large enough to show centrality differences, small enough for real-time rendering

## 5–8 Minute Judge Demonstration Flow

### [0:00-0:30] Setup & Problem Statement
- **Visual**: BlackBox dashboard with title "AI-Powered Criminal Network Analysis System"
- **Narration**: 
  > "Investigators today face fragmented evidence - FIRs here, call logs there, financial records elsewhere. Connecting the dots manually is slow and error-prone."
  > "BlackBox changes this by automatically extracting people, phones, vehicles, and locations from all evidence sources, then building an evidence-backed network showing how they're connected."
- **Action**: Load Case 001: "Missing person investigation with suspected drug trafficking"

### [0:30-1:30] Evidence Ingestion & Processing
- **Visual**: Upload 5 evidence types sequentially:
  1. FIR PDF (missing person report) 
  2. CDR CSV (call logs showing Rajesh-Priya-Vikram communication)
  3. Financial transaction CSV (bank transfers showing money flow)
  4. Surveillance report text (observations at VIP Road location)
  5. Social media screenshot (Facebook/WhatsApp extracts showing coordination)
- **Visual**: Pipeline status updates showing each stage:
  > OCR Stage: Extracting text from documents...
  > Metadata Stage: Pulling EXIF/GPS/timestamps...
  > Entity Extraction: Finding people, phones, vehicles, locations...
  > Relationship Extraction: Mapping connections between entities...
  > Entity Resolution: Disambiguating aliases like "Rajesh Kumar" vs "Raju"...
  > Graph Analytics: Building network and calculating influence...
- **Narration**:
  > "As each piece of evidence is processed, BlackBox extracts the key actors and their connections. Notice how it handles aliases - 'Rajesh Kumar' and 'Raju' are correctly identified as the same person because they share the same phone number."

### [1:30-3:00] Graph Emergence & Key Insights
- **Visual**: Force-directed graph appears with nodes/edges materializing
  - Node colors: Persons (blue), Phones (green), Vehicles (orange), Locations (purple), Orgs (red)
  - Node size: Larger = higher betweenness centrality
  - Edge thickness: Thicker = higher confidence relationship
  - Edge style: Solid = high confidence, Dashed = medium, Dotted = low/unconfirmed
- **Action**: Click on highest-centrality node (Priya Sharma)
- **Visual**: Side panel slides in showing:
  ```
  Entity: Priya Sharma
  Type: Person
  Resolution Confidence: 0.94 [█████████░]
  
  Aliases: Priya
  Phones: +91 87654 32109
  Addresses: 456 Palace Colony, Bhopal
  
  Connected To: 8 entities via 12 relationships
  
  EVIDENCE TRAIL:
  • "Complainant Priya Sharma..." (Finding #FIR_001 - Conf: 0.95)
  • "Priya Sharma is director of Shyam Traders..." (Finding #FIN_RECORDS - Conf: 0.90)
  • "Transaction to A002 of 75,000 INR..." (Finding #FIN_TXNS - Conf: 0.93)
  • "Observed at 456 Palace Colony..." (Finding #SURV_001 - Conf: 0.88)
  ```
- **Visual**: Highlight Priya's connections in the graph:
  - Rajesh Kumar (supplier) - "calls" relationship
  - Vikram Singh (courier) - "calls" relationship  
  - Shyam Traders (organization) - "registered_as_director_of"
  - 456 Palace Colony (residence) - "associated_with"
  - Palace Colony Bus Stand (location) - "associated_with"
  - Sarafa Bazar Jewelry Market (location) - "associated_with"
  - Financial Account A001 (business) - "transfers_money_to"
  - Financial Account A002 (personal) - "deposits_cash_in"
- **Narration**:
  > "Priya Sharma emerges as the central financial and logistical hub in this network - not the drug supplier or the courier, but the person connecting them. The system shows us exactly why: her high betweenness centrality means she bridges the supplier network with the financial and operational networks."
  > "Every connection here is backed by evidence. Click any relationship to see the source documents and confidence scores."

### [3:00-4:30] Pattern Detection & Alerts
- **Visual**: Pattern alerts panel activates with color-coded cards:
  - 🔴 **CALL-TRANSFER-DELIVERY SEQUENCE DETECTED** (Confidence: 0.91)
    - Rajesh → Priya (call) → Money Transfer → Vikram (delivery)
    - Evidence: CDR timestamps + financial transactions + surveillance reports
  - 🔴 **TEMPORAL SPIKE: 200% CALL INCREASE** (Confidence: 0.88)
    - Priya-Rajesh communications spike before financial transfers
    - Evidence: CDR logs showing baseline 2-3 calls/week → 6-8 calls in 2-day window
  - 🔴 **LOCATION REUSE AT CONSISTENT TIMES** (Confidence: 0.93)
    - Location L003 used repeatedly at 23:50-00:30 for exchanges
    - Evidence: Multiple surveillance reports at same time window
  - 🔴 **BURNER PHONE USAGE** (Confidence: 0.86)
    - Vikram uses disposable PH021 for short calls before deliveries
    - Evidence: CDRs showing <60s calls to unknown numbers followed by delivery activity
- **Action**: Click each alert to see detailed evidence trail and timing analysis
- **Narration**:
  > "BlackBox doesn't just show the network - it identifies suspicious patterns that warrant investigator attention. Notice how each alert includes the specific evidence trail and confidence level."
  > "These aren't black-box alerts - you can trace each pattern back to the raw evidence that triggered it."

### [4:30-6:00] Cross-case Investigation & Natural Language Query
- **Visual**: Switch to Case 002: "Separate money laundering investigation"
- **Visual**: Show Case 2 graph with Sameer Khan (money launderer) network
- **Action**: Click "Cross-case connections" button
- **Visual**: System highlights connections between cases:
  - Entity: Pooja Sharma (P005) appears in both Case 001 and Case 002
  - Evidence Trail: 
    - Case 001: "Investigating officer for E001-E007" (Finding #FIRS - Conf: 0.95)
    - Case 002: "Consulted on Case 2 by Financial Intelligence Officer" (Finding #OFFICER_EXCHANGE - Conf: 0.93)
    - Case 002: "Shared intelligence on financial patterns" (Finding #INTELLIGENCE_SHARING - Conf: 0.91)
  - Explanation: "Official information sharing between investigating officers creates a legitimate bridge between investigations"
- **Visual**: Demonstrate investigator natural language query:
  - User types in box: "Who connects the drug supplier in Case 1 and the money launderer in Case 2?"
  - System shows processing indicator → returns results in 2.3 seconds
- **Visual**: Results show:
  - Subgraph highlighted in main view: Rajesh Kumar → Priya Sharma → Pooja Sharma → Deepak Mehta → Sameer Khan
  - Explanation box: "Connection path: Rajesh Kumar (P001) called Priya Sharma (P002), who consulted with Pooja Sharma (P005) on Case 2, who shared intelligence with Deepak Mehta (P007), who analyzed financial transactions for Sameer Khan (P012)."
  - Evidence trail section:
    1. "Rajesh Kumar called Priya Sharma" - CDR_WEEK1/WEEK2 (Conf: 0.94)
    2. "Priya Sharma consulted on Case 2" - OFFICER_EXCHANGE_RECORDS (Conf: 0.93)
    3. "Deepak Mehta shared intelligence on Case 2" - INTELLIGENCE_SHARING_LOGS (Conf: 0.91)
    4. "Deepak Mehta analyzed Sameer Khan's finances" - FINANCIAL_INTELLIGENCE_CASE2 (Conf: 0.89)
- **Narration**:
  > "Now let's see how BlackBox handles cross-case intelligence. When we switch to what appears to be a separate money laundering investigation, the system immediately identifies Pooja Sharma as appearing in both cases."
  > "But more powerfully, our investigator can ask questions in plain English. When we asked 'Who connects the drug supplier in Case 1 and the money launderer in Case 2?', BlackBox traced the legitimate connection through official channels - not through criminal activity, but through proper police consultation and intelligence sharing."
  > "Again, every step in this chain traces back to specific evidence documents with confidence scores."

### [6:00-7:30] Closing & Impact
- **Visual**: Return to Case 001 graph, click on Rajesh Kumar (the actual drug supplier)
- **Visual**: Trace evidence chain in real-time:
  1. Rajesh Kumar → (CDR_WEEK1: "Called Priya Sharma 8:45 PM") → Priya Sharma
  2. Priya Sharma → (FIN_TXNS: "NEFT 75,000 INR to A002 9:02 PM") → Financial Account A002
  3. Financial Account A002 → (SURV_002: "Cash deposit 20,000 INR 10:15 PM") → Vikram Singh (via surveillance)
  4. Vikram Singh → (SURV_002: "Observed delivering package to L004 10:45 PM") → Location L004 (Bus Stand)
- **Narration**:
  > "Let's trace one complete criminal sequence from start to finish. Starting with our actual drug supplier Rajesh Kumar..."
  > "Notice how each step in this chain is backed by specific evidence with timestamps and confidence scores. This isn't speculation - it's an evidence-backed reconstruction of what likely happened."
  > "Most importantly, BlackBox doesn't replace investigators - it gives them superhuman connectivity vision. Instead of spending hours cross-referencing documents, they can instantly see networks, patterns, and connections - all with full evidence traceability."
- **Visual**: Show final validation metrics overlay:
  ```
  VALIDATION AGAINST GROUND TRUTH:
  • Entity Extraction: 92% Precision, 88% Recall, 90% F1
  • Relationship Extraction: 85% Precision, 80% Recall, 82% F1  
  • Entity Resolution: 95% of aliases correctly merged, <2% false merges
  • Pattern Detection: 8/10 ground truth patterns flagged, 0 false positives on legitimate activity
  • Average Latency: 3.2 seconds per evidence item
  ```
- **Final Message** (on screen with naration):
  > "BlackBox: Where every connection in the network traces back to the source evidence."
  > "Not a black box - a transparent lens for seeing what's already there in the evidence."
- **Action**: Hold final screen for 5 seconds, then end.

## Separated Feature Categories

### MUST HAVE for SIH Finals (Implement All)
1. Persistent canonical entity storage (`intel.entities` table)
2. Entity resolution/disambiguation with confidence scoring
3. Evidence-backed relationship storage (`intel.entity_relationships` table)  
4. Network construction using NetworkX
5. Centrality/importance scoring (betweenness centrality primary)
6. Suspicious temporal/spatial pattern detection (5 specific patterns)
7. Graph API endpoints (`/graph`, `/analysis/influencers`, `/analysis/patterns`)
8. Investigator-facing React graph UI with click-to-evidence-trace
9. Exact evidence provenance from graph node/edge to source text
10. Ground-truth precision/recall/F1 evaluation framework
11. End-to-end demo workflow showing investigator value
12. Natural language query endpoint for 3 predefined shapes
13. Cross-case shared entity detection via SQL joins
14. Entity mention tracking (`intel.entity_mentions` table)

### SHOULD HAVE if Time Permits (Implement if MUST HAVEs Complete Early)
1. Temporal relationship timestamps (extract dates/times from evidence text)
2. Uncertainty visualization in graph (dashed lines for low-confidence edges)
3. Entity detail panel showing all aliases, phones, addresses, source evidence
4. Timeline view of events extracted from evidence (chronological)
5. Simple contradiction detector (same phone used by two "different" people)
6. Evidence confidence scoring by source type (FIR > CDR > social media > witness)
7. Export graph as JSON/CSV for external analysis
8. Basic authentication layer (placeholder username/password for demo)

### WOW FEATURES (Only Attempt if ALL MUST HAVEs and SHOULD HAVEs Complete)
1. Real-time streaming simulation (show graph building as evidence processes)
2. "Show me similar patterns" button finding entities with similar connection profiles
3. Anomaly detection highlighting: impossible travel times, sudden relationship formation
4. Cross-case temporal alignment showing correlated activities across cases
5. Voice-to-query investigator interface (push-to-talk microphone in UI)
6. Model confidence calibration showing precision/recall against ground truth

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

## Critical Success Factors for SIH Victory

### What Judges Will See and Remember
1. **Explainability**: "I clicked on this connection and saw exactly which document it came from"
2. **Red Herring Resilience**: "The system correctly ignored the look-alike legitimate business"
3. **Natural Language Query**: "I asked a plain English question and got a visualized answer with evidence"
4. **Pattern Detection**: "It automatically flagged the suspicious call-transfer-delivery sequence"
5. **Centrality Identification**: "It correctly identified the real hub (Priya) not the obvious suspect (Rajesh)"
6. **End-to-End Traceability**: "From evidence upload to graph insight, I saw the complete pipeline"
7. **Validation Metrics**: "92% entity extraction accuracy against adversarial ground truth"
8. **Honest Limitations**: "They showed us what's working and what's not - no fake capabilities"

### Common Pitfalls to Avoid
- ❌ **Fake Intelligence**: Never show mock/LLM-faked results as real
- ❌ **Broken Traceability**: Every graph claim must have evidence backing
- ❌ **Over-Complexity**: Simple working features beat impressive-but-broken ones
- ❌ **Ignoring Red Herrings**: System must demonstrate it doesn't fall for planted look-alikes
- ❌ **Poor Performance**: Demo must work smoothly (<5s latency, responsive UI)
- ❌ **Missing Centrality**: Must show real graph algorithms, not just node/edge counts
- ❌ **Weak NL Query**: If implemented, must work for the 3 predefined shapes reliably
- ❌ **No Validation**: Must have ground truth metrics to back up claims

### Demo Day Preparedness
- **Pre-loaded evidence**: Have demo dataset ready to upload instantly
- **Backup system**: Pre-built Docker image in case of environment issues
- **Talking points**: Emphasize explainability and evidence backing
- **Failure modes**: Know what to show if LLM is slow (spaCy fallback) or graph is large (sampling)
- **Metrics ready**: Have validation report printed to show judges
- **Rehearsed flow**: Know exactly where to click and what to say at each stage

**STOP - Awaiting your approval before proceeding with implementation.**