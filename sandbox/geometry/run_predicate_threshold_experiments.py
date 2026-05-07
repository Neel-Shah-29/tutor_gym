#!/usr/bin/env python3
"""Run clean geometry experiments over predicate-threshold settings and build plots."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_thresholds(raw: str) -> list[int]:
    thresholds = []
    for piece in raw.split(","):
        piece = piece.strip()
        if not piece:
            continue
        thresholds.append(int(piece))
    if not thresholds:
        raise ValueError("At least one predicate threshold is required.")
    return thresholds


def run(cmd: list[str], cwd: Path) -> None:
    print("\n[run_predicate_threshold_experiments] Command:")
    print(" ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parents[2]
    pyafm_dir = workspace_root / "pyAFM"

    parser = argparse.ArgumentParser(
        description="Run geometry experiments over predicate-threshold settings and generate plots."
    )
    parser.add_argument("--n-agents", type=int, default=1)
    parser.add_argument("--n-problems", type=int, default=5)
    parser.add_argument("--thresholds", default="1,3,5", help="Comma-separated predicate thresholds.")
    parser.add_argument("--default-threshold", type=int, default=5)
    parser.add_argument("--when-learner", default="stand")
    parser.add_argument("--process-learner", default="htnlearner")
    parser.add_argument("--track-rollout-preseqs", action="store_true", default=True)
    parser.add_argument("--num-incorrect-force-demo", type=int, default=3)
    parser.add_argument("--agent-seed-base", type=int, default=1000)
    parser.add_argument("--agent-seed-step", type=int, default=1)
    parser.add_argument(
        "--nl-hint-delivery",
        default="demo_only",
        choices=["off", "demo_only", "feedback_only", "demo_and_feedback"],
    )
    parser.add_argument("--use-hf-llm", action="store_true", default=True)
    parser.add_argument("--no-use-hf-llm", action="store_false", dest="use_hf_llm")
    parser.add_argument("--llm-seed", type=int, default=17)
    parser.add_argument("--llm-temperature", type=float, default=0.2)
    parser.add_argument(
        "--log-root-dir",
        default=str(script_dir / "logs_predicate_threshold_experiments"),
        help="Fresh root directory for threshold sweep logs.",
    )
    parser.add_argument(
        "--artifact-dir",
        default=str(pyafm_dir / "geometry_predicate_threshold_artifacts"),
        help="Output directory for aggregated CSV/TSV and plots.",
    )
    parser.add_argument(
        "--llm-cache-dir",
        default=str(script_dir / ".llm_cache_predicate_threshold_experiments"),
        help="Directory for cached LLM responses.",
    )
    parser.add_argument("--clean", action="store_true", default=True)
    parser.add_argument("--no-clean", action="store_false", dest="clean")
    parser.add_argument("--openai-api-key", default="")
    parser.add_argument("--monotonic-envelope", action="store_true")
    args = parser.parse_args()

    thresholds = parse_thresholds(args.thresholds)
    if args.default_threshold not in thresholds:
        raise ValueError("--default-threshold must be included in --thresholds")

    log_root_dir = Path(args.log_root_dir).resolve()
    artifact_dir = Path(args.artifact_dir).resolve()
    llm_cache_dir = Path(args.llm_cache_dir).resolve()

    if args.clean:
        for path in [log_root_dir, artifact_dir]:
            if path.exists():
                shutil.rmtree(path)

    log_root_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    llm_cache_dir.mkdir(parents=True, exist_ok=True)

    run_three = script_dir / "run_three_framework_experiments.py"
    aggregate_three = script_dir / "aggregate_three_framework_logs.py"
    aggregate_thresholds = script_dir / "aggregate_threshold_sweep_logs.py"
    pyafm_overall = pyafm_dir / "geometry_learning_curves_three_frameworks.py"
    pyafm_thresholds = pyafm_dir / "geometry_threshold_sweep_curves.py"

    for threshold in thresholds:
        threshold_log_root = log_root_dir / f"threshold_{threshold}"
        threshold_seed = args.llm_seed + threshold

        cmd = [
            sys.executable,
            str(run_three),
            "--n-agents",
            str(args.n_agents),
            "--n-problems",
            str(args.n_problems),
            "--process-learner",
            args.process_learner,
            "--when-learner",
            args.when_learner,
            "--track-rollout-preseqs",
            "--num-incorrect-force-demo",
            str(args.num_incorrect_force_demo),
            "--agent-seed-base",
            str(args.agent_seed_base),
            "--agent-seed-step",
            str(args.agent_seed_step),
            "--nl-hint-delivery",
            args.nl_hint_delivery,
            "--predicate-threshold",
            str(threshold),
            "--llm-seed",
            str(threshold_seed),
            "--llm-temperature",
            str(args.llm_temperature),
            "--llm-cache-dir",
            str(llm_cache_dir),
            "--log-root-dir",
            str(threshold_log_root),
        ]
        if args.use_hf_llm:
            cmd.append("--use-hf-llm")
        if args.openai_api_key:
            cmd.extend(["--openai-api-key", args.openai_api_key])
        run(cmd, script_dir)

        threshold_csv = artifact_dir / f"threshold_{threshold}_aggregated.csv"
        threshold_tsv = artifact_dir / f"threshold_{threshold}_aggregated.txt"
        run(
            [
                sys.executable,
                str(aggregate_three),
                "--log-root-dir",
                str(threshold_log_root),
                "--output-csv",
                str(threshold_csv),
                "--output-tsv",
                str(threshold_tsv),
            ],
            script_dir,
        )

    combined_csv = artifact_dir / "geometry_threshold_sweep_aggregated.csv"
    combined_tsv = artifact_dir / "geometry_threshold_sweep_aggregated.txt"
    run(
        [
            sys.executable,
            str(aggregate_thresholds),
            "--log-root-dir",
            str(log_root_dir),
            "--output-csv",
            str(combined_csv),
            "--output-tsv",
            str(combined_tsv),
        ],
        script_dir,
    )

    default_tsv = artifact_dir / f"threshold_{args.default_threshold}_aggregated.txt"
    default_overall_plot = artifact_dir / "geometry_learning_curve_3_frameworks.png"
    default_per_hint_dir = artifact_dir / "geometry_learning_curves_by_hint_3_frameworks"
    default_per_hint_csv = artifact_dir / "geometry_learning_curves_by_hint_3_frameworks.csv"
    run(
        [
            sys.executable,
            str(pyafm_overall),
            "--aggregated-input",
            str(default_tsv),
            "--overall-plot",
            str(default_overall_plot),
            "--per-hint-dir",
            str(default_per_hint_dir),
            "--hint-curves-csv",
            str(default_per_hint_csv),
            *(["--monotonic-envelope"] if args.monotonic_envelope else []),
        ],
        pyafm_dir,
    )

    threshold_plot_dir = artifact_dir / "threshold_sweep_curves"
    run(
        [
            sys.executable,
            str(pyafm_thresholds),
            "--aggregated-input",
            str(combined_tsv),
            "--output-dir",
            str(threshold_plot_dir),
            *(["--monotonic-envelope"] if args.monotonic_envelope else []),
        ],
        pyafm_dir,
    )

    print("\n[run_predicate_threshold_experiments] Finished.")
    print(f"Logs root: {log_root_dir}")
    print(f"Artifacts: {artifact_dir}")


if __name__ == "__main__":
    main()
