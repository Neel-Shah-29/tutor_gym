#!/usr/bin/env bash
set -euo pipefail

"$(cd "$(dirname "$0")" && pwd)/run_geometry_tmux_shard.sh" 10 14
