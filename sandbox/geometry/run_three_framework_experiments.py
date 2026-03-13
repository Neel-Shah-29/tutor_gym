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


def build_env(workspace_root: Path) -> dict[str, str]:
    env = os.environ.copy()
    py_paths = [
        str(workspace_root / "AL_Core"),
        str(workspace_root / "tutor_gym"),
        str(workspace_root / "tutor_gym" / "Cognitive-Rule-Engine"),
        str(workspace_root.parent / "STAND"),
    ]
    existing = env.get("PYTHONPATH")
    if existing:
        py_paths.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(py_paths)
    return env


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run geometry experiments for all three training frameworks."
    )
    parser.add_argument("--n-problems", type=int, default=15, help="number of problems per experiment")
    parser.add_argument("--n-fracs", type=int, default=2, help="passed through to run_al_copy_2.py")
    parser.add_argument(
        "--log-root-dir",
        default="log_al_3_frameworks",
        help="Root directory containing per-framework subfolders.",
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
        "--no-unicode-wchar-patch",
        dest="unicode_wchar_patch",
        action="store_false",
        help="pass --no-unicode-wchar-patch to run_al_copy_2.py",
    )
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    workspace_root = script_dir.parents[2]
    run_script = script_dir / "run_al_copy_2.py"

    env = build_env(workspace_root)
    log_root_dir = script_dir / args.log_root_dir
    log_root_dir.mkdir(parents=True, exist_ok=True)

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
            "--when-learner",
            args.when_learner,
            "--num-incorrect-force-demo",
            str(args.num_incorrect_force_demo),
            "--training-framework",
            framework,
            "--log-dir",
            str(log_dir),
        ]
        if args.safe_train:
            cmd.append("--safe-train")
        if args.unicode_fallback:
            cmd.append("--unicode-fallback")
        if args.when_weight_debug:
            cmd.append("--when-weight-debug")
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
