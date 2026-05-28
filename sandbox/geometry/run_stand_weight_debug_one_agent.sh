#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GEOM_DIR="$ROOT_DIR/tutor_gym/sandbox/geometry"
PY="${PYTHON:-$ROOT_DIR/.venv/bin/python}"

if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3 || command -v python)"
fi

AGENT_INDEX="${AGENT_INDEX:-0}"
AGENT_SEED="${AGENT_SEED:-1000}"
THRESHOLD="${THRESHOLD:-3}"
MAX_OPPORTUNITIES="${MAX_OPPORTUNITIES:-10}"
N_PROBLEMS="${N_PROBLEMS:-5}"
DEBUG_HOLDOUT_COUNT="${DEBUG_HOLDOUT_COUNT:-2}"
DEBUG_WARMUP_PROBLEMS="${DEBUG_WARMUP_PROBLEMS:-1}"
USE_HF_LLM="${USE_HF_LLM:-1}"
OUT_ROOT="${OUT_ROOT:-$GEOM_DIR/stand_weight_debug_threshold_${THRESHOLD}_agent$(printf '%02d' "$AGENT_INDEX")}"
LOG_DIR="$OUT_ROOT/logs"
DEBUG_DIR="$OUT_ROOT/per_skill"
STDOUT_LOG="$OUT_ROOT/run_output.txt"
LLM_CACHE_DIR="${LLM_CACHE_DIR:-$ROOT_DIR/.codex_geometry_cache/geometry20/llm_outputs/stand_weight_debug_threshold_${THRESHOLD}_agent$(printf '%02d' "$AGENT_INDEX")}"

mkdir -p "$LOG_DIR" "$DEBUG_DIR" "$LLM_CACHE_DIR"

export PYTHONPATH="$ROOT_DIR/AL_Core:$ROOT_DIR/tutor_gym:$ROOT_DIR/tutor_gym/Cognitive-Rule-Engine:$ROOT_DIR/STAND${PYTHONPATH:+:$PYTHONPATH}"
export CRE_STAND_WEIGHT_DEBUG="${CRE_STAND_WEIGHT_DEBUG:-1}"
export CRE_STAND_TREE_DEBUG="${CRE_STAND_TREE_DEBUG:-0}"
export CRE_STAND_PREDICATE_DEBUG="${CRE_STAND_PREDICATE_DEBUG:-1}"

{
  echo "[$(date)] Starting STAND weight debug run"
  echo "OUT_ROOT=$OUT_ROOT"
  echo "LOG_DIR=$LOG_DIR"
  echo "DEBUG_DIR=$DEBUG_DIR"
  echo "LLM_CACHE_DIR=$LLM_CACHE_DIR"
  echo "DEBUG_HOLDOUT_COUNT=$DEBUG_HOLDOUT_COUNT"
  echo "DEBUG_WARMUP_PROBLEMS=$DEBUG_WARMUP_PROBLEMS"

  llm_args=()
  if [[ "$USE_HF_LLM" != "0" ]]; then
    llm_args+=(--use-hf-llm)
  fi

  "$PY" "$GEOM_DIR/run_al_copy_2.py" \
    --train --train-only \
    --n-problems "$N_PROBLEMS" \
    --n-fracs 2 \
    --n-agents 1 \
    --agent-index-base "$AGENT_INDEX" \
    --agent-seed "$AGENT_SEED" \
    --when-learner stand \
    --process-learner htnlearner \
    --track-rollout-preseqs \
    --num-incorrect-force-demo 3 \
    --training-framework feedback_and_nl_hint \
    --nl-hint-delivery demo_and_feedback \
    --predicate-threshold "$THRESHOLD" \
    --max-learning-opportunities "$MAX_OPPORTUNITIES" \
    --debug-warmup-problems "$DEBUG_WARMUP_PROBLEMS" \
    --log-dir "$LOG_DIR" \
    --stand-debug-dir "$DEBUG_DIR" \
    --holdout-count "$DEBUG_HOLDOUT_COUNT" \
    --holdout-eval-mode stepwise \
    --llm-seed 20 \
    --llm-temperature 0 \
    --llm-cache-dir "$LLM_CACHE_DIR" \
    "${llm_args[@]}" \
    --unicode-wchar-patch \
    --when-weight-debug

  echo "[$(date)] Finished STAND weight debug run"
  echo "Per-skill debug files: $DEBUG_DIR"
} 2>&1 | tee "$STDOUT_LOG"
