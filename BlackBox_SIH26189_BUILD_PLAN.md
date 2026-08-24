# BlackBox × SIH26189 — Gap Analysis & Hackathon Build Plan

**PS 26189 (Ministry of Home Affairs):** *AI-Powered Criminal Network Analysis System*
**Repo:** [Aditya0850/BlackBox](https://github.com/Aditya0850/BlackBox)

---

## 1. Reality check: you're much further along than the README says

The README calls this "Slice 1 — Project Foundation," but the actual codebase has real functionality already:

| Layer | What's actually implemented |
|---|---|
| **Case management** | Full CRUD — create, get, list, update, close, archive (`api/v1/cases.py`, 5 endpoints, clean use-case layer) |
| **Evidence management** | Upload, download, get, list, link/unlink to cases, delete (`api/v1/evidence.py`, 7 endpoints) |
| **Chain of custody** | `intel.analysis_snapshots` — versioned, hash-verified, `is_current` flag, supersession tracking, investigator approval workflow. This is genuinely good forensic design. |
| **Pipeline architecture** | Real plugin pipeline: `integrity_check` → `metadata_extraction` → `ocr_stage` → `ai_summary`, orchestrated via `pipeline/orchestrator.py` with a clean `PipelineStage` protocol |
| **OCR** | Working Tesseract integration (`TesseractOCRProvider`), not a stub |
| **Metadata extraction** | EXIF, GPS, camera model, timestamps, PDF page counts |
| **Audit** | Separate `audit` schema, append-only by design |
| **"AI" summary** | **This is the one weak link** — `ai_summary.py` takes an `llm_client` parameter but never calls it. It's currently keyword-matching (`if "gun" in text_lower: points.append("weapon mentioned")`). No real model call happens yet. |
| **Frontend** | Literally a 15-line placeholder (`<h1>BlackBox Frontend</h1>`). Nothing built. |
| **Entity extraction / Knowledge graph / Cross-case intelligence / MO detection** | Not started — correctly deferred to `ROADMAP.md` v2/v3, which is the right call for a personal project, but it's exactly what SIH26189 is asking for. |

**Bottom line:** your backend forensic infrastructure (custody, versioning, pipeline plugin architecture) is already more rigorous than most SIH finalist teams will have on day 2 of the hackathon. Your gap is entirely in the **intelligence layer** (real AI, not keyword matching) and the **entire frontend**.

---

## 2. What PS26189 actually asks for vs. what you have

Ministry of Home Affairs' stated intent (from the theme + `product.md`'s own vision, which already anticipated this) is a system that:

1. Ingests case-related documents/data
2. Extracts entities (people, phones, vehicles, locations, orgs) and relationships between them
3. Builds a network/graph view of a criminal network
4. Surfaces non-obvious connections a human analyst would miss
5. Is explainable and evidence-traceable (not a black box — literally the opposite of your app's name, use that irony in the pitch)

| PS26189 requirement | BlackBox status | Hackathon action |
|---|---|---|
| Document ingestion | ✅ Done (evidence upload pipeline) | Reuse as-is |
| Entity extraction (people, phones, orgs, locations) | ❌ Not started (roadmap v2) | **Build this — Priority 1** |
| Relationship extraction | ❌ Not started (roadmap v2) | **Build this — Priority 1** |
| Knowledge graph storage + visualization | ❌ Not started (roadmap v2) | **Build this — Priority 2** |
| Cross-case intelligence / similarity | ❌ Not started (roadmap v3, explicitly marked "needs real data to tune, don't build prematurely") | **Fake it for demo — see §4** |
| Modus Operandi detection | ❌ Not started (roadmap v3) | **Fake it for demo — see §4** |
| Explainable AI / evidence traceability | ✅ Architecturally ready (Findings → Snapshots → Evidence chain already exists) | Wire the new entities into this existing chain — don't rebuild it |
| Real LLM-backed reasoning | ⚠️ Stubbed | **Replace stub with real LLM calls — Priority 1** |
| UI to actually see any of this | ❌ Nothing | **Priority 1 — this is your demo surface** |

---

## 3. Team assignment (matches your existing architecture, doesn't fight it)

**Backend dev 1 — Entity & Relationship Extraction pipeline stage**
Add a new `EntityExtractionStage` to the existing pipeline (`pipeline/stages/`), following the exact same `PipelineStage` protocol as `ocr_stage.py`. This is the natural next stage after OCR — feed OCR text + metadata into an LLM (or spaCy NER for speed) to extract:
- People (names)
- Phone numbers, vehicle plates, addresses
- Organizations
- Relationships between them ("X called Y", "X owns vehicle Y")

Store as new tables: `intel.entities`, `intel.entity_relationships` — exactly as your own `ROADMAP.md` already specced them. Each entity/relationship must carry a `finding_id` or `snapshot_id` FK back to its source — this reuses your existing traceability chain, don't invent a new one.

**Backend dev 2 — Real AI Summary + Knowledge Graph API**
1. Fix `ai_summary.py`: wire the existing `llm_client` parameter to an actual API call (any LLM API). Replace the keyword-matching functions with real prompted extraction. This alone is a meaningful and fast win.
2. Build a `GET /api/v1/cases/{id}/graph` endpoint that assembles all entities + relationships for a case into a node/edge JSON structure for the frontend.

**Designer + 1 backend (frontend pairing) — The UI (this doesn't exist at all yet)**
This is your biggest build item and your biggest demo payoff. Minimum viable frontend:
1. Case list / case detail view (wire to already-working case API)
2. Evidence upload + list view (wire to already-working evidence API)
3. **The knowledge graph view** — force-directed graph (react-force-graph or cytoscape.js) rendering the `/graph` endpoint. This is the screen judges will remember.
4. Click a node → side panel showing the source evidence and finding it came from (this is your "explainable AI, not a black box" moment — use your own product.md's "no hallucinations, evidence-backed" philosophy explicitly in the pitch)

**Testers (both) — own three things, not just "testing"**
1. Build a realistic mock case dataset (5–10 fake FIRs/witness statements/call logs with an intentionally hidden network connection to reveal in the demo)
2. Verify chain-of-custody integrity holds under the new entity pipeline stage — every entity must be traceable to source
3. Stress-test the extraction pipeline against messy/ambiguous input so the live demo doesn't break on stage

**Presenters (both)**
Script the demo as a story, not a feature tour: "Investigator uploads 8 case documents. Watch BlackBox extract entities and reveal a hidden connection between two suspects that appeared in separate documents." Rehearse this exact flow against your mock dataset so it's reliable live.

---

## 4. What to fake vs. build for real (be honest about this internally)

You have ~36–48 hours. Be deliberate about where you spend real engineering effort vs. where you build a convincing, honest demo:

**Build for real:**
- Entity/relationship extraction (Priority 1 — this is your technical core)
- Knowledge graph storage + visualization
- Real LLM call replacing the summary stub

**Demo-scope, don't over-engineer:**
- Cross-case intelligence / MO detection — your own `ROADMAP.md` correctly says this needs a real corpus of cases to tune weights on. For the demo, it's fine to implement a simple, honest version (e.g. shared entity overlap between two cases = "possible connection") rather than the full multi-layer similarity engine. **Say this explicitly to judges** — "the full similarity engine needs real case data to calibrate against, here's the architecture for it and a working simplified version" reads as engineering maturity, not a shortcut. Judges who've built real systems respect this more than a team pretending a hackathon-weekend model is production-grade.

**Don't touch:**
- Video/audio/face recognition, fingerprint/DNA/ballistics — your own roadmap explicitly marks these out of scope until entity extraction is stable. Don't let scope creep in under pressure.

---

## 5. Why this pitch wins

Your unfair advantage over every other team attempting this PS: you're not describing a system, you're **demoing chain-of-custody-grade evidence traceability that already exists**, live, under a knowledge graph that assembles in front of the judges. Most teams building "criminal network analysis" in a hackathon will fake the whole backend. You'll have real hash-verified evidence storage, a real audit trail, and a real pipeline architecture underneath a very demoable graph UI — and you can prove it by clicking any node back to its source document.

Lead the pitch with that irony deliberately: *"We called it BlackBox, but the entire point is that nothing in it is a black box — every AI conclusion traces back to the evidence it came from."*
