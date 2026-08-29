# Validation Commands for BlackBox Adversarial Evaluation

This document provides the exact commands that Hermes should use to validate Claude Code's implementation of the BlackBox system using the adversarial test plans.

## Prerequisites
- BlackBox application running and accessible (API at `http://localhost:8000` or as configured)
- Python 3.8+ installed for evaluation harness scripts
- Required Python packages: `requests`, `PyYAML`, `pytest` (for test running)
- Directory structure as defined in `EVALUATION_HARNESS_PLAN.md` must exist

## 1. Setup Evaluation Harness

Run these commands once to set up the evaluation harness directory structure:

```bash
# Navigate to BlackBox root
cd /a/BlackBox

# Create evaluation harness directories
mkdir -p evaluation_harness/{test_data,ground_truth,scripts,results}

# Create empty script files (to be filled with actual implementation later)
touch evaluation_harness/scripts/generate_test_data.py
touch evaluation_harness/scripts/run_blackbox_pipeline.py
touch evaluation_harness/scripts/validate_output.py
touch evaluation_harness/scripts/calculate_metrics.py
touch evaluation_harness/scripts/run_full_evaluation.py
touch evaluation_harness/scripts/run_performance_benchmark.py

# Create config file
cat > evaluation_harness/config.yaml << 'EOF'
blackbox:
  api_url: "http://localhost:8000"
  upload_endpoint: "/api/v1/evidence/upload"
  case_creation_endpoint: "/api/v1/cases"
  # Direct DB connection not used in API mode
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
  output_dir: "./evaluation_harness/results"
  formats: ["json", "html"]
EOF
```

## 2. Generate Test Data

Generate test data for all adversarial test categories:

```bash
# Generate all test data
python evaluation_harness/scripts/generate_test_data.py --category all --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth

# Or generate specific categories
python evaluation_harness/scripts/generate_test_data.py --category entity_resolution --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category entity_extraction --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category relationship_extraction --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category llm_safety --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category provenance --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category graph_tests --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category pattern_detection --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
python evaluation_harness/scripts/generate_test_data.py --category cross_case --output-dir evaluation_harness/test_data --ground-truth-dir evaluation_harness/ground_truth
```

## 3. Run Full Evaluation

Execute the complete adversarial test suite:

```bash
# Run full evaluation with verbose output
python evaluation_harness/scripts/run_full_evaluation.py --config evaluation_harness/config.yaml --verbose

# Run full evaluation and output results to results directory
python evaluation_harness/scripts/run_full_evaluation.py --config evaluation_harness/config.yaml --output-dir evaluation_harness/results
```

## 4. Run Specific Test Categories

Run validation for specific adversarial test categories:

```bash
# Run only entity resolution tests
python evaluation_harness/scripts/run_full_evaluation.py --config evaluation_harness/config.yaml --category entity_resolution --verbose

# Run entity extraction and relationship extraction together
python evaluation_harness/scripts/run_full_evaluation.py --config evaluation_harness/config.yaml --category entity_extraction relationship_extraction --verbose

# Run LLM safety tests
python evaluation_harness/scripts/run_full_evaluation.py --config evaluation_harness/config.yaml --category llm_safety --verbose
```

## 5. Validate Specific Test Cases

Validate individual test cases (useful for debugging):

```bash
# Validate a specific test case
python evaluation_harness/scripts/validate_output.py \
  --test-case er_same_name_001 \
  --test-data-dir evaluation_harness/test_data/entity_resolution/same_name_people \
  --ground-truth-file evaluation_harness/ground_truth/entity_resolution/same_name_people.json \
  --system-output-dir evaluation_harness/results/latest/run_er_same_name_001 \
  --output-format json

# Validate all test cases in a category
python evaluation_harness/scripts/validate_output.py \
  --category entity_resolution \
  --test-data-dir evaluation_harness/test_data/entity_resolution \
  --ground-truth-dir evaluation_harness/ground_truth/entity_resolution \
  --system-output-dir evaluation_harness/results/latest \
  --output-dir evaluation_harness/results/entity_resolution
```

## 6. Calculate Metrics

Compute metrics from validation results:

```bash
# Calculate metrics for all test cases in a category
python evaluation_harness/scripts/calculate_metrics.py \
  --category entity_resolution \
  --input-dir evaluation_harness/results/entity_resolution \
  --output-file evaluation_harness/results/entity_resolution_metrics.json

# Calculate aggregate metrics across all categories
python evaluation_harness/scripts/calculate_metrics.py \
  --all-categories \
  --input-dir evaluation_harness/results \
  --output-file evaluation_harness/results/aggregate_metrics.json
```

## 7. Performance Benchmarks

Run performance benchmarks at different scales:

```bash
# Benchmark with 100 evidence files
python evaluation_harness/scripts/run_performance_benchmark.py \
  --scale 100 \
  --config evaluation_harness/config.yaml \
  --output-file evaluation_harness/results/benchmark_100.json

# Benchmark with 1,000 evidence files
python evaluation_harness/scripts/run_performance_benchmark.py \
  --scale 1000 \
  --config evaluation_harness/config.yaml \
  --output-file evaluation_harness/results/benchmark_1000.json

# Benchmark with 5,000 evidence files
python evaluation_harness/scripts/run_performance_benchmark.py \
  --scale 5000 \
  --config evaluation_harness/config.yaml \
  --output-file evaluation_harness/results/benchmark_5000.json

# Benchmark with 20,000+ evidence files
python evaluation_harness/scripts/run_performance_benchmark.py \
  --scale 20000 \
  --config evaluation_harness/config.yaml \
  --output-file evaluation_harness/results/benchmark_20000.json
```

## 8. Check Evaluation Results

After running evaluation, check the results:

```bash
# View the latest evaluation summary
cat evaluation_harness/results/latest/summary.json

# View detailed HTML report (if generated)
# Open evaluation_harness/results/latest/report.html in a browser

# Check if any critical tests failed
python -c "
import json
with open('evaluation_harness/results/latest/summary.json') as f:
    data = json.load(f)
if data.get('failed_critical', 0) > 0:
    print('CRITICAL FAILURES DETECTED')
    exit(1)
else:
    print('All critical tests passed')
    exit(0)
"
```

## 9. Cleanup (Optional)

Clean up evaluation artifacts:

```bash
# Remove generated test data (keep ground truth if needed)
rm -rf evaluation_harness/test_data/*

# Remove result files
rm -rf evaluation_harness/results/*

# Remove generated evidence from BlackBox (if using API mode and wanting to reset)
# Note: This requires BlackBox API endpoint for cleanup - not included in harness
```

## 10. Script Implementation Notes

The actual Python scripts referenced in these commands must be implemented by Hermes following the designs in `EVALUATION_HARNESS_PLAN.md`. The scripts should:

1. **generate_test_data.py**: Create synthetic evidence files (text, PDF, images) with known ground truth injections for each test category.
2. **run_blackbox_pipeline.py**: Upload evidence via BlackBox API, trigger pipeline, wait for completion, and extract system output.
3. **validate_output.py**: Compare system output against ground truth and produce validation results.
4. **calculate_metrics.py**: Compute precision, recall, F1, provenance coverage, and other metrics from validation results.
5. **run_full_evaluation.py**: Orchestrate test data generation, pipeline execution, validation, and metrics calculation for specified categories.
6. **run_performance_benchmark.py**: Generate large-scale test datasets and measure processing throughput and resource usage.

All scripts must read configuration from `config.yaml` and be placed in `evaluation_harness/scripts/`.

## 11. Passing Criteria

The validation is considered successful if:
- All critical adversarial tests pass (no false merges, no hallucinations, provenance intact)
- Entity precision/recall/F1 ≥ thresholds defined in config.yaml
- Relationship precision/recall/F1 ≥ thresholds
- Entity-resolution merge precision/recall ≥ thresholds
- Provenance coverage ≥ threshold
- Pattern detection precision/recall/F1 ≥ thresholds
- Performance benchmarks meet max time/memory constraints
- No regressions in existing BlackBox functionality (run existing unit tests separately)

--- 
*End of Validation Commands Document*