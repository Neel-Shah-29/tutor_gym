#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
GEOM_DIR="$ROOT_DIR/tutor_gym/sandbox/geometry"
SESSION="${SESSION:-geometry20}"
LOG_ROOT="${LOG_ROOT:-$GEOM_DIR/logs_predicate_threshold_experiments_20_agents}"

mkdir -p "$LOG_ROOT/script_outputs"

if tmux has-session -t "$SESSION" 2>/dev/null; then
  echo "tmux session '$SESSION' already exists." >&2
  echo "Attach with: tmux attach -t $SESSION" >&2
  exit 1
fi

tmux new-session -d -s "$SESSION" -n agents_00_04 \
  "cd '$ROOT_DIR' && '$GEOM_DIR/run_geometry_tmux_agents_00_04.sh'"

tmux new-window -t "$SESSION" -n agents_05_09 \
  "cd '$ROOT_DIR' && '$GEOM_DIR/run_geometry_tmux_agents_05_09.sh'"

tmux new-window -t "$SESSION" -n agents_10_14 \
  "cd '$ROOT_DIR' && '$GEOM_DIR/run_geometry_tmux_agents_10_14.sh'"

tmux new-window -t "$SESSION" -n agents_15_19 \
  "cd '$ROOT_DIR' && '$GEOM_DIR/run_geometry_tmux_agents_15_19.sh'"

echo "Started tmux session: $SESSION"
echo "Attach: tmux attach -t $SESSION"
echo "Detach after attaching: Ctrl-b d"
echo "Script outputs: $LOG_ROOT/script_outputs"
