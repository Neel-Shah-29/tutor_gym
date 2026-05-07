#!/usr/bin/env python3
"""Run geometry experiments for multiple NL-hint delivery settings."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


DELIVERY_MODES = ("demo_only", "feedback_only")


def run(cmd: list[str], cwd: Path) -> None:
    print("\n[run_hint_delivery_experiments] Command:")
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(
        description="Run geometry experiments for multiple NL-hint delivery settings."
    )
    parser.add_argument("--n-agents", type=int, default=10)
    parser.add_argument("--n-problems", type=int, default=5)
    parser.add_argument("--predicate-threshold", type=int, default=5)
    parser.add_argument("--when-learner", default="stand")
    parser.add_argument("--process-learner", default="htnlearner")
    parser.add_argument("--track-rollout-preseqs", action="store_true", default=True)
    parser.add_argument("--num-incorrect-force-demo", type=int, default=3)
    parser.add_argument("--agent-seed-base", type=int, default=1000)
    parser.add_argument("--agent-seed-step", type=int, default=1)
    parser.add_argument("--holdout-count", type=int, default=0)
    parser.add_argument(
        "--holdout-eval-mode",
        default="stepwise",
        choices=["off", "next_problem", "stepwise"],
    )
    parser.add_argument("--use-hf-llm", action="store_true", default=True)
    parser.add_argument("--llm-seed", type=int, default=17)
    parser.add_argument("--llm-temperature", type=float, default=0.2)
    parser.add_argument("--llm-cache-dir", default="")
    parser.add_argument("--openai-api-key", default="")
    parser.add_argument(
        "--log-root-dir",
        default=str(script_dir / "logs_hint_delivery_experiments"),
        help="Root directory that will contain one subdirectory per hint-delivery mode.",
    )
    args = parser.parse_args()

    run_three = script_dir / "run_three_framework_experiments.py"
    log_root_dir = Path(args.log_root_dir).resolve()
    log_root_dir.mkdir(parents=True, exist_ok=True)

    for delivery in DELIVERY_MODES:
        delivery_root = log_root_dir / delivery
        cmd = [
            sys.executable,
            str(run_three),
            "--n-agents",
            str(args.n_agents),
            "--n-problems",
            str(args.n_problems),
            "--predicate-threshold",
            str(args.predicate_threshold),
            "--when-learner",
            args.when_learner,
            "--process-learner",
            args.process_learner,
            "--num-incorrect-force-demo",
            str(args.num_incorrect_force_demo),
            "--agent-seed-base",
            str(args.agent_seed_base),
            "--agent-seed-step",
            str(args.agent_seed_step),
            "--nl-hint-delivery",
            delivery,
            "--holdout-count",
            str(args.holdout_count),
            "--holdout-eval-mode",
            args.holdout_eval_mode,
            "--log-root-dir",
            str(delivery_root),
        ]
        if args.track_rollout_preseqs:
            cmd.append("--track-rollout-preseqs")
        if args.use_hf_llm:
            cmd.append("--use-hf-llm")
        if args.llm_seed is not None:
            cmd.extend(["--llm-seed", str(args.llm_seed)])
        if args.llm_temperature is not None:
            cmd.extend(["--llm-temperature", str(args.llm_temperature)])
        if args.llm_cache_dir:
            cmd.extend(["--llm-cache-dir", args.llm_cache_dir])
        if args.openai_api_key:
            cmd.extend(["--openai-api-key", args.openai_api_key])
        run(cmd, script_dir)


if __name__ == "__main__":
    main()
