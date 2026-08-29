# Evaluation Harness Plan for BlackBox Criminal Network Analysis System

This document describes the complete evaluation harness that will be used to run the adversarial tests defined in ADVERSARIAL_TEST_PLAN.md against Claude Code's implementation. This includes test data generation, execution procedures, validation scripts, and metrics collection.

## OVERVIEW

The evaluation harness consists of:
1. **Test Data Generator**: Creates synthetic evidence files with known ground truth for each test case.
2. **Test Executor**: Runs the BlackBox pipeline on test data and collects outputs.
3. **Validator**: Compares system outputs against expected ground truth and calculates metrics.
4. **Reporter**: Generates detailed pass/fail reports and metric summaries.

All components are designed to be run as independent scripts that do not modify the BlackBox application code.

## 1. TEST DATA GENERATOR

### 1.1 Directory Structure
```
evaluation_harness/
├── test_data/
│   ├── entity_resolution/
│   │   ├── same_name_people/
│   │   ├── aliases/
│   │   ├── ... (each test category)
│   ├── entity_extraction/
│   ├── relationship_extraction/
│   ├── llm_safety/
│   ├── provenance/
│   ├── graph_tests/
│   ├── pattern_detection/
│   └── cross_case/
├── ground_truth/
│   ├── entity_resolution/
│   │   ├── same_name_people.json
│   │   └── ...
│   ├── entity_extraction.json
│   ├── relationship_extraction.json
│   ├── ... (one per test category)
├── scripts/
│   ├── generate_test_data.py
│   ├── run_blackbox_pipeline.py
│   ├── validate_output.py
│   ├── calculate_metrics.py
│   └── run_full_evaluation.py
├── config.yaml
└README.md
```

###  (this file)
```

### 1.2 Test Data Format
Each test case will have:
- **Input Evidence**: One or more files (PDF, image, text) in the test_data subdirectory.
- **Ground Truth**: JSON file defining expected entities, relationships, and attributes.

Example ground truth structure:
```json
{
  "test_case_id": "er_same_name_001",
  "description": "Two different people with same name",
  "evidence_files": ["firm_001.txt", "cdr_005.txt"],
  "expected_entities": [
    {
      "canonical_id": "ent_001",
      "name": "Rajesh Kumar (Engineer)",
      "aliases": ["Rajesh Kumar"],
      "entity_type": "person",
      "attributes": {
        "phone": "9876543210",
        "occupation": "engineer"
      },
      "source_evidence": "firm_001.txt",
      "text_span": [0, 13]
    },
    {
      "canonical_id": "ent_002",
      "name": "Rajesh Kumar (Shop Owner)",
      "aliases": ["Rajesh Kumar"],
      "entity_type": "person",
      "attributes": {
        "phone": "8765432109",
        "occupation": "shop_owner"
      },
      "source_evidence": "cdr_005.txt",
      "text_span": [5, 18]
    }
  ],
  "expected_relationships": [],
  "expected_merges": [],
  "expected_splits": [],
  "pattern_flags": []
}
```

### 1.3 Data Generation Script
`generate_test_data.py` will:
- Create synthetic text, PDF, and image evidence files.
- Inject known entities, relationships, and test patterns.
- Generate corresponding ground truth JSON.
- Support OCR corruption via image manipulation (blur, noise, smudge).
- Create multilingual and transliteration variations.

## 2. TEST EXECUTOR

### 2.1 Pipeline Runner
`run_blackbox_pipeline.py` will:
- Take a test case directory as input.
- Upload all evidence files to BlackBox via the API (or direct DB insert if API not available, but preference is to test via API).
- Trigger the pipeline (if not automatic on upload).
- Wait for processing to complete (polling for analysis snapshot status).
- Extract the final state: entities, relationships, graph, provenance.
- Output raw results to a temporary directory for validation.

### 2.2 Execution Modes
- **API Mode**: Upload via `/api/v1/evidence/upload`, link to case, trigger pipeline.
- **Direct DB Mode** (fallback): Insert evidence record directly, call pipeline orchestrator.
- **Configurable** via `config.yaml`.

## 3. VALIDATOR

### 3.1 Output Comparison
`validate_output.py` will:
- Load system output and ground truth for a test case.
- Compare entities:
  - Match by canonical ID or by attributes (name, type, aliases).
  - Check for correct merges/splits.
  - Validate provenance (text span, evidence ID).
- Compare relationships:
  - Match subject, predicate, object.
  - Validate confidence scores and provenance.
- Check graph structure:
  - Node count matches entity count.
  - Edge count matches relationship count.
  - Verify centrality calculations if applicable.
- Check pattern detection flags.
- Output detailed diff and pass/fail status.

### 3.2 Provenance Validation
Special checks:
- For every entity in output, verify:
  - `evidence_id` exists and is valid.
  - `text_start` and `text_end` are within bounds of the OCR text.
  - The substring matches the entity text (allowing for OCR errors in the source).
- For relationships, verify linkage to entity mentions.

## 4. METRICS CALCULATOR

`calculate_metrics.py` will compute:
- Entity precision, recall, F1 per test case and aggregated.
- Relationship precision, recall, F1.
- Entity-resolution merge precision and recall.
- Provenance coverage percentage.
- Pattern detection precision, recall, F1.
- Processing throughput (evidence/second, records/second).

## 5. FULL EVALUATION RUNNER

`run_full_evaluation.py` will:
- Parse command line arguments (specific test categories, verbosity, etc.).
- For each test category:
  1. Generate test data (if not already present or if `--regenerate`).
  2. Run BlackBox pipeline on all test cases in the category.
  3. Validate outputs and calculate metrics.
  4. Store results.
- Aggregate metrics across all test cases.
- Generate final report (JSON and HTML).
- Exit with non-zero code if any critical test fails or metrics below threshold.

### 5.1 Configuration (`config.yaml`)
```yaml
blackbox:
  api_url: "http://localhost:8000"
  upload_endpoint: "/api/v1/evidence/upload"
  case_creation_endpoint: "/api/v1/cases"
  # Or direct DB connection details
test_data:
  base_path: "./evaluation_harness/test_data"
  ground_truth_path: "./evaluation_harness/ground_truth"
  cleanup_after_run: false
validation:
  entity_thresholds:
    precision_min: 0.85
    recall_min: 0.80
    f1_min: 0.82
  relationship_thresholds:
    precision_min: 0.80
    recall_min: 0.75
    f1_min: 0.77
  merge_thresholds:
    precision_min: 0.90
    recall_min: 0.85
  provenance_threshold:
    coverage_min: 0.95
  pattern_thresholds:
    precision_min: 0.80
    recall_min: 0.75
    f1_min: 0.77
  performance:
    max_time_per_100_evidence: 30  # seconds
    max_memory_mb: 1024
reporting:
  output_dir: "./evaluation_results"
  formats: ["json", "html"]
```

## 6. EXACT COMMANDS FOR VALIDATION

### 6.1 Setup (Run Once)
```bash
# Clone evaluation harness (if separate repo) or ensure directories exist
cd /a/BlackBox
mkdir -p evaluation_harness/{test_data,ground_truth,scripts}
# Copy or create the scripts as defined below
```

### 6.2 Generate Test Data
```bash
python evaluation_harness/scripts/generate_test_data.py --category all
# Or specific category:
python evaluation_harness/scripts/generate_test_data.py --category entity_resolution
```

### 6.3 Run Full Evaluation
```bash
python evaluation_harness/scripts/run_full_evaluation.py --verbose
```

### 6.4 Run Specific Test Category
```bash
python evaluation_harness/scripts/run_full_evaluation.py --category entity_extraction --verbose
```

### 6.5 Validate Only (if test data and system output already exist)
```bash
python evaluation_harness/scripts/validate_output.py --test-case er_same_name_001
python evaluation_harness/scripts/calculate_metrics.py --category entity_resolution
```

### 6.6 Check Performance Benchmarks
```bash
python evaluation_harness/scripts/run_performance_benchmark.py --scale 100
python evaluation_harness/scripts/run_performance_benchmark.py --scale 1000
```

## 7. SCRIPT OUTLINES (TO BE IMPLEMENTED BY HERMES LATER)

### 7.1 generate_test_data.py
```python
# Pseudocode
def generate_entity_resolution_tests():
    for test_case in ER_TEST_CASES:
        # Create evidence files with specific name variations
        # Create ground truth JSON
        pass

def generate_ocr_noise():
    # Use PIL to add blur, noise, smudge to text images
    pass
```

### 7.2 run_blackbox_pipeline.py
```python
# Pseudocode
def run_test_case(test_case_dir):
    # Upload evidence files via API
    # Create case and link evidence
    # Wait for pipeline completion (poll /api/v1/analysis_snapshots)
    # Fetch findings and construct entity/relationship graph
    # Save output JSON
    pass
```

### 7.3 validate_output.py
```python
# Pseudocode
def validate_entity_resolution(system_output, ground_truth):
    # Match entities
    # Calculate TP, FP, FN for merges
    # Check provenance
    # Return validation result
    pass
```

### 7.4 calculate_metrics.py
```python
# Pseudocode
def calculate_prf(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
    return precision, recall, f1
```

## 8. PASS/FAIL CRITERIA FOR HARNESS ITSELF

The evaluation harness is considered ready if:
- All scripts are syntactically correct Python (no import errors).
- Test data generation produces valid files and JSON.
- The pipeline runner can successfully upload evidence and trigger processing (assuming BlackBox API is running).
- Validator can compare outputs and produce metrics.
- Full evaluation runs without crashing and produces a report.

## 9. SECURITY AND ISOLATION

- The evaluation harness runs as a separate process; does not modify BlackBox source.
- Test data is stored in `evaluation_harness/` directory.
- If using API mode, interacts only with exposed endpoints.
- No direct modification of database or application files.

## 10. EXTENSIBILITY

New test categories can be added by:
1. Adding a new subdirectory under `test_data/` and `ground_truth/`.
2. Extending `generate_test_data.py` with a new generator function.
3. Ensuring `validate_output.py` can handle the new ground truth structure.
4. Adding threshold defaults in `config.yaml` if needed.

---

*This evaluation harness is designed to be a black-box validation tool. It treats the BlackBox system as an opaque entity to be tested via its inputs (evidence files) and outputs (API responses, database state, or exported reports).*

*Do not modify BlackBox application code when implementing or running this harness.*