# BlackBox SIH26189 Implementation Plan

Based on gap analysis of BlackBox_SIH26189_BUILD_PLAN.md vs current codebase

## EXISTING STRENGTHS (DO NOT MODIFY)
- Case management CRUD (5 endpoints)
- Evidence management (7 endpoints)  
- Chain of custody: intel.analysis_snapshots (versioned, hash-verified)
- Pipeline: integrity_check → metadata_extraction → ocr_stage → ai_summary
- Working Tesseract OCR
- Metadata extraction: EXIF, GPS, timestamps, PDF page counts
- Audit schema: append-only design
- Traceability chain: Findings → Snapshots → Evidence

## BACKEND TASKS

### 1. Entity Extraction Pipeline Stage (Priority 1)
**File:** `backend/src/pipeline/stages/entity_extraction.py`
**Requirements:**
- Follow PipelineStage protocol (like ocr_stage.py)
- Input: OCR text + metadata from previous stage
- Extract: People, phones, vehicles, locations, orgs, relationships
- Store: New tables `intel.entities`, `intel.entity_relationships` 
- Traceability: FK to source findings/snapshots
- Integration: Add to pipeline orchestrator after ocr_stage

### 2. Fix AI Summary Stage (Priority 1)  
**File:** `backend/src/pipeline/stages/ai_summary.py`
**Requirements:**
- Wire existing llm_client parameter to actual API call
- Replace keyword-matching with proper LLM prompted extraction
- Maintain traceability to source evidence

### 3. Knowledge Graph API Endpoint (Priority 2)
**File:** `backend/src/api/v1/cases.py` (or new graph endpoint file)
**Requirements:**
- Endpoint: `GET /api/v1/cases/{id}/graph`
- Response: JSON nodes (entities) + edges (relationships) for case
- Format: Compatible with react-force-graph/cytoscape.js

## FRONTEND TASKS (Priority 1 - Biggest Gap)

### 4. Case Management Views
- Case list page (using existing case API)
- Case detail view with case info + evidence list

### 5. Evidence Management Views  
- Evidence upload component (using existing evidence API)
- Evidence list view showing uploaded files

### 6. Knowledge Graph Visualization
- Install: react-force-graph or cytoscape.js
- Component fetching from `/api/v1/cases/{id}/graph`
- Force-directed graph rendering entities/relationships
- Node click handler → show side panel

### 7. Traceability Side Panel
- On node click: fetch source evidence/finding details
- Display: source excerpt, finding/snapshot ID, custody verification
- Show extract quote linking entity to source document

## TESTING & PREPARATION

### 8. Mock Dataset Creation
- 5-10 fake documents: FIRs, witness statements, call logs
- Intentional hidden network connection to reveal in demo
- Varied formats (PDF, images, text) for pipeline testing

### 9. Integrity Verification
- Test every entity links back to source evidence
- Verify chain-of-custody properties through new stage
- Test audit trail integrity

### 10. Pipeline Stress Testing
- Test with messy/ambiguous inputs
- Ensure demo won't break on stage
- Performance testing

## PRESENTATION

### 11. Demo Script
- Flow: "Investigator uploads 8 case documents..."
- Rehearse revealing hidden suspect connection
- Explain traceability: "Every AI conclusion traces back to evidence"
- Show: upload → processing → graph reveal → node click → source proof

## WHAT TO BUILD VS FAKE

**BUILD FOR REAL:**
- Entity/relationship extraction (technical core)
- Knowledge graph storage + visualization
- Real LLM call in summary stage

**DEMO-SCOPE (HONEST):**
- Cross-case intelligence / MO detection: simple shared-entity version
- Explicitly tell judges: "Full similarity engine needs real data; here's architecture + simplified working version"

**DON'T TOUCH:**
- Video/audio/face recognition, fingerprint/DNA/ballistics (per roadmap)