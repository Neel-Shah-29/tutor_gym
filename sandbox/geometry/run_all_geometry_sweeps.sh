#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GEOM_DIR="$ROOT_DIR/tutor_gym/sandbox/geometry"
PYAFM_DIR="$ROOT_DIR/pyAFM"

PY="${PYTHON:-$ROOT_DIR/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PY="$(command -v python3)"
  elif command -v python >/dev/null 2>&1; then
    PY="$(command -v python)"
  else
    echo "No Python interpreter found." >&2
    exit 1
  fi
fi

N_AGENTS="${N_AGENTS:-5}"
N_PROBLEMS="${N_PROBLEMS:-5}"
N_FRACS="${N_FRACS:-2}"
WHEN_LEARNER="${WHEN_LEARNER:-stand}"
PROCESS_LEARNER="${PROCESS_LEARNER:-htnlearner}"
NUM_INCORRECT_FORCE_DEMO="${NUM_INCORRECT_FORCE_DEMO:-3}"
AGENT_SEED_BASE="${AGENT_SEED_BASE:-1000}"
AGENT_SEED_STEP="${AGENT_SEED_STEP:-1}"

PREDICATE_THRESHOLDS="${PREDICATE_THRESHOLDS:-1,3,5}"
DEFAULT_THRESHOLD="${DEFAULT_THRESHOLD:-5}"
HINT_DELIVERY_PREDICATE_THRESHOLD="${HINT_DELIVERY_PREDICATE_THRESHOLD:-5}"
NL_HINT_DELIVERY_MODES="${NL_HINT_DELIVERY_MODES:-off demo_only feedback_only demo_and_feedback}"

USE_HINT_LLM="${USE_HINT_LLM:-1}"
LLM_SEED="${LLM_SEED:-17}"
LLM_TEMPERATURE="${LLM_TEMPERATURE:-0}"
LLM_CACHE_DIR="${LLM_CACHE_DIR:-$ROOT_DIR/.codex_geometry_cache/full_geometry_sweeps/llm_outputs}"

CLEAN="${CLEAN:-1}"
MONOTONIC_ENVELOPE="${MONOTONIC_ENVELOPE:-0}"
AGGREGATION_MODE="${AGGREGATION_MODE:-concat}"
VARIABILITY_BAND="${VARIABILITY_BAND:-sem}"

THRESHOLD_LOG_ROOT="${THRESHOLD_LOG_ROOT:-$GEOM_DIR/logs_predicate_threshold_experiments_all}"
THRESHOLD_ARTIFACT_DIR="${THRESHOLD_ARTIFACT_DIR:-$PYAFM_DIR/geometry_predicate_threshold_artifacts_all}"
HINT_DELIVERY_LOG_ROOT="${HINT_DELIVERY_LOG_ROOT:-$GEOM_DIR/logs_hint_delivery_experiments_all}"
HINT_DELIVERY_ARTIFACT_ROOT="${HINT_DELIVERY_ARTIFACT_ROOT:-$GEOM_DIR/plots_hint_delivery_experiments_all}"

mkdir -p "$LLM_CACHE_DIR"

run() {
  echo
  echo "[run_all_geometry_sweeps] $*"
  "$@"
}

metric_output_stem() {
  case "$1" in
    correct_rate)
      printf '%s\n' "correct_rate"
      ;;
    assistance_rate)
      printf '%s\n' "assistance_rate"
      ;;
    correct+hint_rate)
      printf '%s\n' "correct_hint_rate"
      ;;
    *)
      printf '%s\n' "$1"
      ;;
  esac
}

common_llm_args=(
  --llm-seed "$LLM_SEED"
  --llm-temperature "$LLM_TEMPERATURE"
  --llm-cache-dir "$LLM_CACHE_DIR"
)

if [[ "$USE_HINT_LLM" == "1" ]]; then
  common_llm_args+=(--use-hf-llm)
fi

pyafm_extra_args=()
if [[ "$MONOTONIC_ENVELOPE" == "1" ]]; then
  pyafm_extra_args+=(--monotonic-envelope)
fi

threshold_cmd=(
  "$PY" "$GEOM_DIR/run_predicate_threshold_experiments.py"
  --n-agents "$N_AGENTS"
  --n-problems "$N_PROBLEMS"
  --thresholds "$PREDICATE_THRESHOLDS"
  --default-threshold "$DEFAULT_THRESHOLD"
  --when-learner "$WHEN_LEARNER"
  --process-learner "$PROCESS_LEARNER"
  --track-rollout-preseqs
  --num-incorrect-force-demo "$NUM_INCORRECT_FORCE_DEMO"
  --agent-seed-base "$AGENT_SEED_BASE"
  --agent-seed-step "$AGENT_SEED_STEP"
  --nl-hint-delivery demo_and_feedback
  --log-root-dir "$THRESHOLD_LOG_ROOT"
  --artifact-dir "$THRESHOLD_ARTIFACT_DIR"
  "${common_llm_args[@]}"
  "${pyafm_extra_args[@]}"
)

if [[ "$CLEAN" == "1" ]]; then
  threshold_cmd+=(--clean)
else
  threshold_cmd+=(--no-clean)
fi

run "${threshold_cmd[@]}"

if [[ "$CLEAN" == "1" ]]; then
  rm -rf "$HINT_DELIVERY_LOG_ROOT" "$HINT_DELIVERY_ARTIFACT_ROOT"
fi
mkdir -p "$HINT_DELIVERY_LOG_ROOT" "$HINT_DELIVERY_ARTIFACT_ROOT"

IFS=' ' read -r -a delivery_modes <<< "$NL_HINT_DELIVERY_MODES"

for delivery in "${delivery_modes[@]}"; do
  log_root="$HINT_DELIVERY_LOG_ROOT/$delivery"
  out_root="$HINT_DELIVERY_ARTIFACT_ROOT/$delivery"
  cache_root="$ROOT_DIR/.codex_geometry_cache/logs_hint_delivery_experiments_all/$delivery"

  mkdir -p "$log_root" "$out_root" "$cache_root"

  run_three_cmd=(
    "$PY" "$GEOM_DIR/run_three_framework_experiments.py"
    --n-agents "$N_AGENTS"
    --n-problems "$N_PROBLEMS"
    --n-fracs "$N_FRACS"
    --when-learner "$WHEN_LEARNER"
    --process-learner "$PROCESS_LEARNER"
    --track-rollout-preseqs
    --num-incorrect-force-demo "$NUM_INCORRECT_FORCE_DEMO"
    --predicate-threshold "$HINT_DELIVERY_PREDICATE_THRESHOLD"
    --nl-hint-delivery "$delivery"
    --agent-seed-base "$AGENT_SEED_BASE"
    --agent-seed-step "$AGENT_SEED_STEP"
    --log-root-dir "$log_root"
    --cache-root-dir "$cache_root"
    "${common_llm_args[@]}"
  )

  run "${run_three_cmd[@]}"

  run "$PY" "$GEOM_DIR/aggregate_three_framework_logs.py" \
    --log-root-dir "$log_root" \
    --output-csv "$out_root/geometry_log_al_3_frameworks_aggregated.csv" \
    --output-tsv "$out_root/geometry_log_al_3_frameworks_aggregated.txt"

  for metric in correct_rate assistance_rate correct+hint_rate; do
    metric_stem="$(metric_output_stem "$metric")"
    plot_cmd=(
      "$PY" "$GEOM_DIR/plot_learning_curves_three_frameworks.py"
      --log-root-dir "$log_root"
      --aggregation-mode "$AGGREGATION_MODE"
      --variability-band "$VARIABILITY_BAND"
      --metric "$metric"
      --output-csv "$out_root/${metric_stem}_curves.csv"
      --output-plot "$out_root/${metric_stem}_curves.png"
    )
    run "${plot_cmd[@]}"
  done

  pyafm_cmd=(
    "$PY" "$PYAFM_DIR/geometry_learning_curves_three_frameworks.py"
    --aggregated-input "$out_root/geometry_log_al_3_frameworks_aggregated.txt"
    --overall-plot "$out_root/geometry_learning_curve_3_frameworks.png"
    --per-hint-dir "$out_root/geometry_learning_curves_by_hint_3_frameworks"
    --hint-curves-csv "$out_root/geometry_learning_curves_by_hint_3_frameworks.csv"
    "${pyafm_extra_args[@]}"
  )
  run "${pyafm_cmd[@]}"
done

echo
echo "Threshold sweep artifacts: $THRESHOLD_ARTIFACT_DIR"
echo "Hint-delivery sweep artifacts: $HINT_DELIVERY_ARTIFACT_ROOT"
