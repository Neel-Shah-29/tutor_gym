#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="/home/nshah621/Tail"
cd "$ROOT_DIR"

OUT_DIR="$ROOT_DIR/pyAFM/geometry_predicate_threshold_artifacts_20_agents/threshold_learning_curves"
LOG_ROOT="$ROOT_DIR/tutor_gym/sandbox/geometry/logs_predicate_threshold_experiments_20_agents"
SCRIPT_OUTPUT_ROOT="$LOG_ROOT/script_outputs"
SCRIPT_OUTPUT="$SCRIPT_OUTPUT_ROOT/generate_curves.txt"

mkdir -p "$OUT_DIR" "$SCRIPT_OUTPUT_ROOT"
exec > >(tee -a "$SCRIPT_OUTPUT") 2>&1

echo "[$(date)] Generating threshold learning curves"
echo "LOG_ROOT=$LOG_ROOT"
echo "OUT_DIR=$OUT_DIR"

for threshold in 1 3 5; do
  echo
  echo "[$(date)] Aggregating threshold $threshold logs"
  .venv/bin/python tutor_gym/sandbox/geometry/aggregate_three_framework_logs.py \
    --log-root-dir "$LOG_ROOT/threshold_${threshold}" \
    --output-csv "$OUT_DIR/threshold_${threshold}_aggregated.csv" \
    --output-tsv "$OUT_DIR/threshold_${threshold}_aggregated.txt"

  echo "[$(date)] Plotting threshold $threshold average error rate"
  .venv/bin/python pyAFM/geometry_learning_curves_three_frameworks.py \
    --aggregated-input "$OUT_DIR/threshold_${threshold}_aggregated.txt" \
    --overall-plot "$OUT_DIR/threshold_${threshold}_geometry_learning_curve_3_frameworks.png" \
    --per-hint-dir "$OUT_DIR/threshold_${threshold}_geometry_learning_curves_by_hint_3_frameworks" \
    --hint-curves-csv "$OUT_DIR/threshold_${threshold}_geometry_learning_curves_by_hint_3_frameworks.csv"
done

echo
echo "[$(date)] Finished generating curves"
echo "Curve script output: $SCRIPT_OUTPUT"
