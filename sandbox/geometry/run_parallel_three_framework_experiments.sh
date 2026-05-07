#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GEOM_DIR="$ROOT_DIR/tutor_gym/sandbox/geometry"
RUN_SCRIPT="$GEOM_DIR/run_al_copy_2.py"
LOG_ROOT_DIR="${1:-$GEOM_DIR/logs_geometry_10_agents_parallel_2probs}"
CACHE_TEMPLATE="${2:-$ROOT_DIR/.codex_geometry_cache/logs_geometry_10_agents_final}"
N_AGENTS="${N_AGENTS:-10}"
N_PROBLEMS="${N_PROBLEMS:-2}"
MAX_PARALLEL="${MAX_PARALLEL:-6}"
NUM_INCORRECT_FORCE_DEMO="${NUM_INCORRECT_FORCE_DEMO:-3}"
PREDICATE_THRESHOLD="${PREDICATE_THRESHOLD:-5}"
NL_HINT_DELIVERY="${NL_HINT_DELIVERY:-demo_only}"
PROCESS_LEARNER="${PROCESS_LEARNER:-htnlearner}"
WHEN_LEARNER="${WHEN_LEARNER:-stand}"
AGENT_SEED_BASE="${AGENT_SEED_BASE:-1000}"
AGENT_SEED_STEP="${AGENT_SEED_STEP:-1}"
USE_HINT_LLM="${USE_HINT_LLM:-0}"
LLM_CACHE_DIR="${LLM_CACHE_DIR:-}"
CACHE_COPY_ROOT="$ROOT_DIR/.codex_geometry_cache/parallel_runs/$(basename "$LOG_ROOT_DIR")"

mkdir -p "$LOG_ROOT_DIR" "$CACHE_COPY_ROOT"
export PYTHONPATH="$ROOT_DIR/AL_Core:$ROOT_DIR/tutor_gym:$ROOT_DIR/tutor_gym/Cognitive-Rule-Engine:$ROOT_DIR/STAND${PYTHONPATH:+:$PYTHONPATH}"

launch_agent() {
  local framework="$1"
  local agent_idx="$2"
  local seed="$3"
  local framework_dir="$LOG_ROOT_DIR/$framework"
  local cache_root="$CACHE_COPY_ROOT/${framework}_agent$(printf '%02d' "$agent_idx")"
  local stdout_log="$framework_dir/agent$(printf '%02d' "$agent_idx").out"
  local -a process_args=()

  mkdir -p "$framework_dir"
  if [[ -d "$CACHE_TEMPLATE" ]]; then
    cp -a "$CACHE_TEMPLATE" "$cache_root"
  else
    mkdir -p "$cache_root"
  fi

  if [[ -n "${PROCESS_LEARNER}" && "${PROCESS_LEARNER,,}" != "none" && "${PROCESS_LEARNER,,}" != "off" ]]; then
    process_args+=(--process-learner "$PROCESS_LEARNER" --track-rollout-preseqs)
  fi
  if [[ "$USE_HINT_LLM" == "1" ]]; then
    process_args+=(--use-hf-llm)
  fi
  if [[ -n "$LLM_CACHE_DIR" ]]; then
    process_args+=(--llm-cache-dir "$LLM_CACHE_DIR")
  fi

  (
    export XDG_CACHE_HOME="$cache_root"
    export NUMBA_CACHE_DIR="$cache_root/numba"
    python "$RUN_SCRIPT" \
      --train --train-only \
      --n-problems "$N_PROBLEMS" \
      --n-fracs 2 \
      --n-agents 1 \
      --agent-index-base "$agent_idx" \
      --agent-seed "$seed" \
      --when-learner "$WHEN_LEARNER" \
      --num-incorrect-force-demo "$NUM_INCORRECT_FORCE_DEMO" \
      --training-framework "$framework" \
      --nl-hint-delivery "$NL_HINT_DELIVERY" \
      --log-dir "$framework_dir" \
      --predicate-threshold "$PREDICATE_THRESHOLD" \
      --holdout-count 0 \
      --holdout-eval-mode stepwise \
      "${process_args[@]}" \
      --unicode-wchar-patch \
      > "$stdout_log" 2>&1
  ) &
}

wait_for_slots() {
  while (( $(jobs -pr | wc -l) >= MAX_PARALLEL )); do
    wait -n
  done
}

for framework in feedback_only nl_hint_only feedback_and_nl_hint; do
  echo "=== Running $framework ==="
  for ((agent_idx=0; agent_idx<N_AGENTS; agent_idx++)); do
    seed=$((AGENT_SEED_BASE + agent_idx * AGENT_SEED_STEP))
    wait_for_slots
    launch_agent "$framework" "$agent_idx" "$seed"
  done
  wait
  echo "=== Completed $framework ==="
done

echo "All experiments completed: $LOG_ROOT_DIR"
