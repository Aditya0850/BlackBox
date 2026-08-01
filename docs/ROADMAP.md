# BlackBox — Roadmap (v2+)

These are complete, user-facing capabilities intentionally deferred past
v1. They are not designed in implementation detail here — v1's
architecture is built so none of these require redesigning the core
(pipeline contract, EvidenceContext, Clean Architecture boundaries,
Human/Machine schema separation). When one of these becomes the current
slice, it gets its own design pass and its own ADR — not before.

Ordering below is roughly by dependency, not commitment — later items
build on earlier ones.

---

## v2 candidates

**Entity & Relationship Extraction**
`intel.entities`, `intel.entity_relationships`. NER stage added to the
pipeline (`EntityExtractor` implementation — e.g. spaCy first). Depends
on: v1's Finding/Snapshot model.

**Knowledge Graph**
Derived projection (materialized view) over `entity_relationships` —
never hand-maintained. Visualization via React Flow. Depends on: Entity
& Relationship Extraction.

**Timeline Reconstruction (dynamic)**
Regenerates automatically as evidence changes, beyond v1's static
per-upload timeline. Depends on: Entity extraction (dates/people tied to
events).

**Investigation Notebook**
`notebook.theories`, `notebook.theory_evidence_links` (schema reserved
in v1, tables built here). Strict rule: AI may suggest, never author —
enforced via DB role grants (pipeline worker has zero grant on
`notebook.*`). Depends on: nothing structurally, but low value before
entities/relationships exist to reason about.

**AI Suggestions**
`intel.ai_suggestions` — pipeline/AI-generated, read-only to Notebook,
becomes Human Knowledge only when an investigator explicitly links it to
a theory. Depends on: Investigation Notebook.

---

## v3 candidates

**Similarity Engine (implementation)**
Interface can be sketched early (`SimilarityEngine` Protocol,
`SimilarityResult` with breakdown/signals/explanation) but the actual
multi-layer weighted fusion — evidence-level (OCR/image embeddings,
perceptual hashes, EXIF), entity-level, timeline-level, case-level — is
real research work requiring real data to tune against. Do not build
until there's a corpus of real cases to validate weights.

**Cross-Case Intelligence**
Uses Similarity Engine to surface related cases with an explanation
("same weapon, same wound pattern, same district..."). Depends on:
Similarity Engine.

**Modus Operandi Detection**
Recurring-pattern detection across cases (weapon usage, entry/exit
methods, geographic hotspots). Depends on: Cross-Case Intelligence.

**Contradiction Detection**
Compares evidence/witness statements/GPS/CCTV timestamps and flags
disagreements without accusing. Depends on: Entity/Timeline extraction
being solid.

**Provenance Graph (implementation)**
Generic `provenance.edges` DAG table (polymorphic, app-level integrity
via contract tests, not DB FKs) so any AI conclusion can be traced back
to raw evidence. In v1, snapshot→evidence lineage is sufficient; this
becomes necessary once findings feed entities, entities feed theories,
and theories feed suggestions — i.e. once there's an actual multi-hop
chain to trace. Depends on: Entities, Notebook, AI Suggestions.

---

## v4 candidates

**Decision Objects**
Immutable object distinct from simple state transitions: id, author,
timestamp, reason, supporting/contradicting evidence, superseded-by —
makes the investigative decision process itself auditable (e.g. "12 Jan:
Person X becomes suspect" → "3 Feb: superseded" → "14 Feb: cleared").
Depends on: Entity state transitions being in regular use.

**Truth & Uncertainty Engine**
A subsystem that continuously recalculates confidence, completeness,
contradictions, and missing evidence at every level (Evidence → Finding
→ Entity → Relationship → Theory → Recommendation) and surfaces concrete
next actions ("Collect fingerprints," "Interview Witness C"). Interface
can be sketched as a `TrustEngine.assess(object_id) -> TrustAssessment`
Protocol when this slice starts. Depends on: enough real entities,
theories, and cases to have something to aggregate — premature before
that.

**Investigation Health Dashboard**
Per-case view: evidence completeness, timeline completeness, witness
coverage, digital evidence coverage, chain-of-custody status,
contradictions, pending verification, overall confidence. Depends on:
Truth & Uncertainty Engine.

**Predictive Investigation Suggestions**
Proactive surfacing of missing evidence, uncollected CCTV, unverified
alibis, likely escape routes. Depends on: Truth & Uncertainty Engine +
Cross-Case Intelligence.

**Trust as a 5th bounded context** (speculative)
If confidence/contradiction/completeness logic starts sprawling across
modules once the Truth & Uncertainty Engine exists, consider promoting
it to its own bounded context (schema + module boundary), the way
Machine/Human Knowledge were split in v1. Not decided — evaluate only
once the logic actually exists and its scatter becomes a real problem,
not preemptively.

---

## Explicitly out of scope until named modules above are stable

Video understanding, audio transcription, face recognition (legal review
required first), fingerprint/DNA/ballistics analysis, call detail
records, financial intelligence, geospatial analysis beyond basic
mapping. These are new evidence *types*, not new subsystems — each would
plug into the existing `PipelineStage` interface the same way OCR does,
which is exactly what v1's plugin architecture is for. No design work
needed here until one is actually prioritized.

---

## Scope discipline (carried over from architecture discussion)

For every item above, before building it: *does this help an
investigator reach the truth faster, or is it just technically
impressive?* If only the latter, it stays here indefinitely.
