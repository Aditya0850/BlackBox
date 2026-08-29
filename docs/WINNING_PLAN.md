# BlackBox × SIH/PS 26189 — Corrected Battle Plan (1-2 week window)

Verified against actual repo code (not README, not assumptions) on 2026-08-25.
Supersedes `BlackBox_SIH26189_BUILD_PLAN.md` and `IMPLEMENTATION_PLAN.md`, which
were both written under a false 36-48hr assumption. You have 1-2 weeks. Build
for real, not for demo-theater.

---

## 1. Verified ground truth (from actual code, not docs)

| Layer | Real status | Evidence |
|---|---|---|
| Case CRUD | ✅ Real, 5 endpoints | `api/v1/cases.py` |
| Evidence CRUD | ✅ Real, 7 endpoints | `api/v1/evidence.py` |
| Chain of custody | ✅ Strong — versioned, hash-verified snapshots | `analysis_snapshots` table |
| OCR | ✅ Real Tesseract | `ocr_stage.py` |
| Metadata extraction | ✅ Real EXIF/GPS/timestamps | `metadata_extraction.py` |
| Pipeline architecture | ✅ Clean, extensible `PipelineStage` protocol | `pipeline/orchestrator.py` |
| Entity extraction | 🟠 Exists but non-functional for purpose — pure regex, no persistence layer at all | `entity_extraction.py`, no `intel.entities` table exists |
| Relationship extraction | 🟠 Same — proximity-heuristic only, not persisted | same file |
| AI summary | 🔴 Fake — `llm_client` param accepted, **never called**. Pure keyword matching. | `ai_summary.py` |
| Knowledge graph (storage/API) | 🔴 Does not exist | no `intel.entity_relationships` table, no `/graph` endpoint |
| Graph visualization | 🔴 Does not exist | frontend is a placeholder |
| Frontend (anything) | 🔴 15-line placeholder, wired to nothing | `App.tsx` |
| Key-influencer / centrality analysis | 🔴 Does not exist | — |
| Cross-case / MO / contradiction detection | 🔴 Does not exist | — |
| Demo dataset | ✅ Genuinely strong — has planted red herrings, aliases, multi-case entities | `demo_data_v2/ground_truth/CANONICAL_ENTITIES_AND_RELATIONSHIPS.json` |
| Tests | 🟡 Decent foundation, ~1900 lines | `backend/src/tests/`, `backend/tests/` |

**Bottom line:** real forensic spine + real eval dataset, zero intelligence layer, zero UI. The gap is 100% in NER/graph/algorithms/frontend — none of which currently has a single line of working code, despite the roadmap docs sounding like architecture exists for it. It doesn't. Build it from the DB schema up.

---

## 2. Why the old plan (36-48hr) was wrong for you now

The existing `BUILD_PLAN.md` told you to **fake** cross-case intelligence and MO detection ("shared entity overlap = possible connection, say it's simplified"). That was correct advice for a 2-day sprint. It is **the wrong call** with 1-2 weeks — faking it now reads as *less* impressive to judges than a working simplified version with a clear roadmap for the full version. With this much time, build the real (if scoped-down) version of everything the PS asks for, using actual graph algorithms, not string-overlap tricks.

---

## 3. Key technical decisions to make now

**Entity/relationship extraction:** Drop the regex approach entirely. Use an LLM-based structured extraction (function-calling / JSON schema output) as the primary extractor — it will correctly handle "Rajesh Kumar" vs "Arjun Malik" alias tricks that regex cannot. Fall back to spaCy NER only if LLM latency/cost becomes a demo problem. Every extracted entity/relationship must carry a `finding_id` back to source text — non-negotiable, this is your explainability story.

**Graph storage:** Don't stand up Neo4j just for storage — Postgres tables (`intel.entities`, `intel.entity_relationships`) are fine and keep your existing audit/traceability model intact. But **do** use `networkx` (pure Python, zero infra cost) to compute real graph algorithms server-side: degree/betweenness centrality, PageRank, community detection (Louvain). This gives you real "key influencer" and "hidden cluster" outputs, not hand-waving, for almost no added infra risk.

**Frontend graph viz:** `react-force-graph` or `cytoscape.js` on top of a new `GET /api/v1/cases/{id}/graph` endpoint. Node click → side panel → source `Finding`/`Snapshot` → this is your single most important demo screen.

---

## 4. Two-week build plan

### Backend track (Claude Code — primary implementation)
**Week 1**
1. New tables: `intel.entities`, `intel.entity_relationships`, `intel.entity_mentions` (FK to `finding_id`). Alembic migration.
2. Rebuild `entity_extraction.py`: LLM-based structured extraction (person/phone/vehicle/location/org + relationship triples), replacing regex. Persist to new tables, not just Finding metadata.
3. Fix `ai_summary.py`: wire the actual LLM call. Delete the keyword-matching functions.
4. `GET /api/v1/cases/{id}/graph` — nodes + edges JSON.
5. `GET /api/v1/cases/{id}/analysis/influencers` — networkx centrality + community detection over the case graph, returns ranked key players with the graph-theoretic reason ("high betweenness — bridges two otherwise disconnected clusters").

**Week 2**
6. Cross-case connection endpoint: shared entity (person/phone/vehicle) appearing in ≥2 cases → real join query, not a heuristic — this genuinely is just correct SQL/graph traversal, not "fake."
7. Simple contradiction/anomaly signals: timestamp overlaps, same phone number used by two "different" people, entity appearing at two locations at conflicting times. Deterministic rule checks over the entity/relationship tables — legitimate, explainable, not ML-hand-waving.
8. Investigator query endpoint: natural-language question → LLM translates to a graph query over the entities/relationships (start narrow: "who connects X and Y", "who is central in this case") — this is your "wow" feature, scope it to 2-3 supported query shapes, don't over-promise open-ended NL-to-Cypher.
9. Load-test/stress-test pipeline against `demo_data_v2` including the red-herring cases — the ground truth JSON is your acceptance test. If BlackBox correctly separates "Rajesh Kumar" (supplier) from name-alike red herrings, that's a strong, honest, demoable claim of accuracy.

### Frontend track (Claude Code, second pass)
1. Case list/detail wired to real API (exists already, just needs a UI).
2. Evidence upload/list wired to real API.
3. **Knowledge graph view** — force-directed, colored by entity type, click node → side panel with source evidence excerpt + confidence + finding ID.
4. Influencer panel — ranked list with the graph-theoretic explanation string from the backend.
5. Timeline view of events extracted across evidence for a case.
6. Investigator query box for the NL query endpoint.

### QA/verification track (Hermes — autonomous manager role, matches what you described)
1. Own `demo_data_v2` as the acceptance test suite — build a script that runs the full pipeline against it and diffs extracted entities/relationships against `CANONICAL_ENTITIES_AND_RELATIONSHIPS.json`, reporting precision/recall. This turns your ground truth into a real evaluation metric you can quote to judges ("94% entity extraction accuracy against a hand-labeled ground truth with adversarial name collisions").
2. Verify every entity persisted traces back to a real `finding_id`/`snapshot_id` — no orphaned/unexplainable graph nodes, ever. This is your core differentiation claim; it must hold under adversarial testing, not just the happy path.
3. Docker Compose end-to-end smoke test daily.
4. Track what Claude Code claims is done vs what actually passes tests — adjudicate scope creep vs real gaps.
5. Own the demo script rehearsal and break it deliberately (bad OCR input, ambiguous names, empty case) so nothing fails live.

---

## 5. What NOT to build (scope discipline, keep the roadmap's own discipline)

Face recognition, audio/video, fingerprint/DNA/ballistics, full multi-layer similarity engine calibration — your own `docs/ROADMAP.md` already correctly excludes these until there's real case-corpus data to tune against. Don't let "we have 2 weeks now" turn into "let's also do face recognition." It won't be good in 2 weeks and it's not what's asked. Depth over feature-count.

---

## 6. Pitch angle

Lead with the irony that's already sitting in the product name: *"We called it BlackBox, but the entire point is that nothing in it is a black box — every entity, every relationship, every 'key influencer' claim traces back through a hash-verified evidence chain to the exact document and sentence it came from."* Then demo it live: upload → extraction → graph assembles → click the ranked-influencer node → source document opens → ask the investigator-query box "who connects Case 1 and Case 2" → get a real graph-traversal answer. Close with the accuracy number from the red-herring ground truth test — that's the line that separates you from teams that faked their backend all weekend.
