#!/usr/bin/env python3
"""Run geometry training in three feedback/hint frameworks with separate log dirs."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


EXPERIMENTS = (
    ("feedback_only", "feedback_only"),
    ("nl_hint_only", "nl_hint_only"),
    ("feedback_and_nl_hint", "feedback_and_nl_hint"),
)


def build_env(workspace_root: Path, local_cache_root: Path | None = None) -> dict[str, str]:
    env = os.environ.copy()
    local_cache_root = local_cache_root or (workspace_root / ".codex_geometry_cache")
    py_paths = [
        str(workspace_root / "AL_Core"),
        str(workspace_root / "tutor_gym"),
        str(workspace_root / "tutor_gym" / "Cognitive-Rule-Engine"),
        str(workspace_root / "STAND"),
    ]
    existing = env.get("PYTHONPATH")
    if existing:
        py_paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(py_paths)
    env.setdefault("XDG_CACHE_HOME", str(local_cache_root))
    env.setdefault("NUMBA_CACHE_DIR", str(local_cache_root / "numba"))
    return env


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run geometry experiments for all three training frameworks."
    )
    parser.add_argument("--n-agents", type=int, default=1, help="number of seeded agent runs per framework")
    parser.add_argument("--n-problems", type=int, default=15, help="number of problems per experiment")
    parser.add_argument("--n-fracs", type=int, default=2, help="passed through to run_al_copy_2.py")
    parser.add_argument("--process-learner", default="htnlearner", help="process learner for agent")
    parser.add_argument("--track-rollout-preseqs", action="store_true", default=True, help="Enable process rollout preseq tracking")
    parser.add_argument("--predicate-threshold", type=int, default=5, help="Maximum predicates to keep for hint gating.")
    parser.add_argument("--agent-seed-base", type=int, default=1000, help="Base random seed for the first agent.")
    parser.add_argument("--agent-seed-step", type=int, default=1, help="Seed increment between agents.")
    parser.add_argument(
        "--nl-hint-delivery",
        default="demo_only",
        choices=["off", "demo_only", "feedback_only", "demo_and_feedback"],
        help="When hint-enabled frameworks receive NL hints.",
    )
    parser.add_argument("--holdout-count", type=int, default=0, help="Number of holdout problems per agent.")
    parser.add_argument(
        "--holdout-eval-mode",
        default="stepwise",
        choices=["off", "next_problem", "stepwise"],
        help="Evaluation mode for optional holdout problems.",
    )
    parser.add_argument(
        "--log-root-dir",
        default="log_al_3_frameworks",
        help="Root directory containing per-framework subfolders.",
    )
    parser.add_argument(
        "--cache-root-dir",
        default="",
        help="Optional isolated cache root for CRE/Numba. Defaults to a workspace-local folder derived from --log-root-dir.",
    )
    parser.add_argument(
        "--when-learner",
        default="stand",
        help="when learner passed to CREAgent",
    )
    parser.add_argument(
        "--num-incorrect-force-demo",
        type=int,
        default=-1,
        help="trainer setting; -1 disables forced demo after incorrect streak",
    )
    parser.add_argument("--safe-train", action="store_true", help="pass --safe-train to run_al_copy_2.py")
    parser.add_argument(
        "--unicode-fallback",
        action="store_true",
        help="pass --unicode-fallback to run_al_copy_2.py",
    )
    parser.add_argument(
        "--unicode-wchar-patch",
        action="store_true",
        default=True,
        help="pass --unicode-wchar-patch to run_al_copy_2.py (default: enabled)",
    )
    parser.add_argument(
        "--when-weight-debug",
        action="store_true",
        help="forward --when-weight-debug to run_al_copy_2.py",
    )
    parser.add_argument(
        "--stand-tree-debug",
        action="store_true",
        help="forward --stand-tree-debug to run_al_copy_2.py",
    )
    parser.add_argument(
        "--no-unicode-wchar-patch",
        dest="unicode_wchar_patch",
        action="store_false",
        help="pass --no-unicode-wchar-patch to run_al_copy_2.py",
    )
    parser.add_argument("--use-hf-llm", action="store_true", help="forward --use-hf-llm to run_al_copy_2.py")
    parser.add_argument("--llm-seed", type=int, default=None, help="Forwarded to run_al_copy_2.py")
    parser.add_argument("--llm-temperature", type=float, default=None, help="Forwarded to run_al_copy_2.py")
    parser.add_argument("--llm-cache-dir", default="", help="Forwarded to run_al_copy_2.py")
    parser.add_argument(
        "--openai-api-key",
        default=os.environ.get("OPENAI_API_KEY", ""),
        help="Optional OpenAI API key passed through to run_al_copy_2.py.",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parents[2]
    run_script = script_dir / "run_al_copy_2.py"

    log_root_dir = Path(args.log_root_dir).resolve()
    log_root_dir.mkdir(parents=True, exist_ok=True)
    cache_root_dir = (
        Path(args.cache_root_dir).resolve()
        if args.cache_root_dir
        else (workspace_root / ".codex_geometry_cache" / log_root_dir.name)
    )
    cache_root_dir.mkdir(parents=True, exist_ok=True)

    env = build_env(workspace_root, local_cache_root=cache_root_dir)
    if args.openai_api_key:
        env["OPENAI_API_KEY"] = args.openai_api_key

    for framework, subfolder_name in EXPERIMENTS:
        log_dir = log_root_dir / subfolder_name
        log_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            sys.executable,
            str(run_script),
            "--train",
            "--train-only",
            "--n-problems",
            str(args.n_problems),
            "--n-fracs",
            str(args.n_fracs),
            "--n-agents",
            str(args.n_agents),
            "--when-learner",
            args.when_learner,
            "--num-incorrect-force-demo",
            str(args.num_incorrect_force_demo),
            "--training-framework",
            framework,
            "--nl-hint-delivery",
            args.nl_hint_delivery,
            "--log-dir",
            str(log_dir),
            "--process-learner",
            args.process_learner,
            "--predicate-threshold",
            str(args.predicate_threshold),
            "--agent-seed-base",
            str(args.agent_seed_base),
            "--agent-seed-step",
            str(args.agent_seed_step),
            "--holdout-count",
            str(args.holdout_count),
            "--holdout-eval-mode",
            args.holdout_eval_mode,
        ]
        if args.safe_train:
            cmd.append("--safe-train")
        if args.unicode_fallback:
            cmd.append("--unicode-fallback")
        if args.when_weight_debug:
            cmd.append("--when-weight-debug")
        if args.stand_tree_debug:
            cmd.append("--stand-tree-debug")
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
        if args.unicode_wchar_patch:
            cmd.append("--unicode-wchar-patch")
        else:
            cmd.append("--no-unicode-wchar-patch")

        print(f"\n=== Running {framework} ===")
        print(f"Log folder: {log_dir}")
        print("Command:", " ".join(cmd))

        subprocess.run(cmd, cwd=str(script_dir), env=env, check=True)

    print("\nAll experiments completed.")
    for framework, subfolder_name in EXPERIMENTS:
        print(f"- {framework}: {log_root_dir / subfolder_name}")


if __name__ == "__main__":
    main()
