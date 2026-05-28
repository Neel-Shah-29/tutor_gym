#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GEOM_DIR="$ROOT_DIR/tutor_gym/sandbox/geometry"
RUN_SCRIPT="$GEOM_DIR/run_al_copy_2.py"

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <start_agent_index> <end_agent_index>" >&2
  echo "Example: $0 0 4" >&2
  exit 1
fi

START_AGENT="$1"
END_AGENT="$2"
SHARD_NAME="$(printf 'agents_%02d_%02d' "$START_AGENT" "$END_AGENT")"

PY="${PYTHON:-$ROOT_DIR/.venv/bin/python}"
if [[ ! -x "$PY" ]]; then
  PY="$(command -v python3 || command -v python)"
fi

N_PROBLEMS="${N_PROBLEMS:-5}"
N_FRACS="${N_FRACS:-2}"
WHEN_LEARNER="${WHEN_LEARNER:-stand}"
PROCESS_LEARNER="${PROCESS_LEARNER:-htnlearner}"
NUM_INCORRECT_FORCE_DEMO="${NUM_INCORRECT_FORCE_DEMO:-3}"
AGENT_SEED_BASE="${AGENT_SEED_BASE:-1000}"
AGENT_SEED_STEP="${AGENT_SEED_STEP:-1}"
PREDICATE_THRESHOLDS="${PREDICATE_THRESHOLDS:-1 3 5}"
NL_HINT_DELIVERY="${NL_HINT_DELIVERY:-demo_and_feedback}"
USE_HINT_LLM="${USE_HINT_LLM:-1}"
LLM_SEED="${LLM_SEED:-17}"
LLM_TEMPERATURE="${LLM_TEMPERATURE:-0}"
LOG_ROOT="${LOG_ROOT:-$GEOM_DIR/logs_predicate_threshold_experiments_20_agents}"
CACHE_ROOT="${CACHE_ROOT:-$ROOT_DIR/.codex_geometry_cache/geometry20}"
SCRIPT_OUTPUT_ROOT="${SCRIPT_OUTPUT_ROOT:-$LOG_ROOT/script_outputs}"

mkdir -p "$SCRIPT_OUTPUT_ROOT"
SCRIPT_OUTPUT="$SCRIPT_OUTPUT_ROOT/${SHARD_NAME}.txt"
exec > >(tee -a "$SCRIPT_OUTPUT") 2>&1

export PYTHONPATH="$ROOT_DIR/AL_Core:$ROOT_DIR/tutor_gym:$ROOT_DIR/tutor_gym/Cognitive-Rule-Engine:$ROOT_DIR/STAND${PYTHONPATH:+:$PYTHONPATH}"

echo "[$(date)] Starting $SHARD_NAME"
echo "ROOT_DIR=$ROOT_DIR"
echo "LOG_ROOT=$LOG_ROOT"
echo "CACHE_ROOT=$CACHE_ROOT"
echo "PREDICATE_THRESHOLDS=$PREDICATE_THRESHOLDS"
echo "NL_HINT_DELIVERY=$NL_HINT_DELIVERY"
echo "Output log: $SCRIPT_OUTPUT"

frameworks=(feedback_only nl_hint_only feedback_and_nl_hint)

launch_agent() {
  local threshold="$1"
  local framework="$2"
  local agent_idx="$3"
  local seed="$4"
  local framework_dir="$LOG_ROOT/threshold_${threshold}/${framework}"
  local agent_tag
  local stdout_log
  local -a llm_args=()

  agent_tag="$(printf 'agent%02d_seed%d' "$agent_idx" "$seed")"
  stdout_log="$framework_dir/${agent_tag}.out"
  mkdir -p "$framework_dir"

  if compgen -G "$framework_dir/frac_*_${agent_tag}_*.txt" >/dev/null; then
    echo "[$(date)] Skipping threshold $threshold $framework $agent_tag; result log already exists."
    return 0
  fi

  if [[ "$USE_HINT_LLM" == "1" ]]; then
    llm_args+=(--use-hf-llm)
  fi

  (
    export XDG_CACHE_HOME="$CACHE_ROOT/threshold_${threshold}/${framework}/agent_${agent_idx}"
    export NUMBA_CACHE_DIR="$XDG_CACHE_HOME/numba"
    mkdir -p "$XDG_CACHE_HOME" "$NUMBA_CACHE_DIR"

    "$PY" "$RUN_SCRIPT" \
      --train --train-only \
      --n-problems "$N_PROBLEMS" \
      --n-fracs "$N_FRACS" \
      --n-agents 1 \
      --agent-index-base "$agent_idx" \
      --agent-seed "$seed" \
      --when-learner "$WHEN_LEARNER" \
      --process-learner "$PROCESS_LEARNER" \
      --track-rollout-preseqs \
      --num-incorrect-force-demo "$NUM_INCORRECT_FORCE_DEMO" \
      --training-framework "$framework" \
      --nl-hint-delivery "$NL_HINT_DELIVERY" \
      --predicate-threshold "$threshold" \
      --log-dir "$framework_dir" \
      --holdout-count 0 \
      --holdout-eval-mode stepwise \
      --llm-seed "$((LLM_SEED + threshold + agent_idx))" \
      --llm-temperature "$LLM_TEMPERATURE" \
      --llm-cache-dir "$CACHE_ROOT/llm_outputs/threshold_${threshold}/${framework}/agent_${agent_idx}" \
      --unicode-wchar-patch \
      "${llm_args[@]}" \
      > "$stdout_log" 2>&1
  ) &
  agent_pids+=("$!")
}

for threshold in $PREDICATE_THRESHOLDS; do
  echo
  echo "[$(date)] === Threshold $threshold ==="
  for framework in "${frameworks[@]}"; do
    echo "[$(date)] Running $framework for agents $START_AGENT-$END_AGENT"
    agent_pids=()
    for ((agent_idx=START_AGENT; agent_idx<=END_AGENT; agent_idx++)); do
      seed=$((AGENT_SEED_BASE + agent_idx * AGENT_SEED_STEP))
      launch_agent "$threshold" "$framework" "$agent_idx" "$seed"
    done
    if ((${#agent_pids[@]} > 0)); then
      wait "${agent_pids[@]}"
    fi
    echo "[$(date)] Completed $framework for threshold $threshold"
  done
done

echo
echo "[$(date)] Finished $SHARD_NAME"
echo "Shard output: $SCRIPT_OUTPUT"
