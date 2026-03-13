#!/usr/bin/env python3
"""Aggregate geometry run logs and plot learning curves for all three criteria."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List

import matplotlib.pyplot as plt


def iter_rows(log_file: Path) -> Iterable[Dict[str, str]]:
    with log_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            return
        headers = reader.fieldnames
        for row in reader:
            if not row:
                continue
            if not any((row.get(key) or "").strip() for key in headers):
                continue
            if all((row.get(key) or "").strip() == key for key in headers):
                continue
            yield {key: (row.get(key) or "").strip() for key in headers}


def iter_log_rows(log_dir: Path) -> Iterable[Dict[str, str]]:
    for log_file in sorted(log_dir.glob("*.txt")):
        for row in iter_rows(log_file):
            row["Source Log File"] = log_file.name
            yield row


def build_learning_curve(rows: Iterable[Dict[str, str]], metric: str):
    correct = 0
    incorrect = 0
    hints = 0
    total = 0

    steps: List[int] = []
    values: List[float] = []
    count_hist: List[Dict[str, int]] = []

    for row in rows:
        outcome = (row.get("Outcome") or "").strip().upper()
        if outcome == "CORRECT":
            correct += 1
        elif outcome == "INCORRECT":
            incorrect += 1
        elif outcome == "HINT":
            hints += 1
        total += 1

        if metric == "correct_rate":
            denom = (correct + incorrect)
            value = correct / denom if denom else 0.0
        elif metric == "assistance_rate":
            value = (hints + incorrect) / total if total else 0.0
        elif metric == "correct+hint_rate":
            value = (correct + hints) / total if total else 0.0
        else:
            denom = (correct + incorrect)
            value = correct / denom if denom else 0.0

        steps.append(total)
        values.append(value)
        count_hist.append(
            {
                "correct": correct,
                "incorrect": incorrect,
                "hints": hints,
                "total": total,
            }
        )

    return steps, values, count_hist


def write_aggregated_csv(path: Path, records: List[Dict[str, object]]) -> None:
    if not records:
        return
    columns = ["framework", "step", "value", "metric", "correct", "incorrect", "hints", "total", "source_log_file"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for record in records:
            writer.writerow(record)


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot geometry learning curves across 3 training criteria.")
    parser.add_argument(
        "--log-root-dir",
        default="log_al_3_frameworks",
        help="Root directory containing per-framework log folders.",
    )
    parser.add_argument("--feedback-only-subdir", default="feedback_only")
    parser.add_argument("--nl-hint-only-subdir", default="nl_hint_only")
    parser.add_argument("--feedback-and-nl-subdir", default="feedback_and_nl_hint")
    parser.add_argument(
        "--metric",
        default="correct_rate",
        choices=["correct_rate", "assistance_rate", "correct+hint_rate"],
        help="Learning curve to plot.",
    )
    parser.add_argument("--output-csv", default="geometry_learning_curves_aggregated.csv")
    parser.add_argument("--output-plot", default="geometry_learning_curves.png")
    parser.add_argument("--workspace-root", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    base = root / args.log_root_dir

    frameworks = {
        "feedback_only": base / args.feedback_only_subdir,
        "nl_hint_only": base / args.nl_hint_only_subdir,
        "feedback_and_nl_hint": base / args.feedback_and_nl_subdir,
    }

    records: List[Dict[str, object]] = []
    fig, ax = plt.subplots(figsize=(9, 5))

    for framework, log_dir in frameworks.items():
        if not log_dir.exists():
            print(f"Skipping missing directory: {log_dir}")
            continue

        steps, values, count_hist = build_learning_curve(iter_log_rows(log_dir), args.metric)
        if not steps:
            print(f"No rows found in {log_dir}")
            continue

        final_counts = count_hist[-1]
        ax.plot(steps, values, label=f"{framework} (n={final_counts['total']})")
        for step_idx, value, counts in zip(steps, values, count_hist):
            source = log_dir.name
            records.append(
                {
                    "framework": framework,
                    "step": step_idx,
                    "value": value,
                    "metric": args.metric,
                    "correct": counts["correct"],
                    "incorrect": counts["incorrect"],
                    "hints": counts["hints"],
                    "total": counts["total"],
                    "source_log_file": source,
                }
            )

    if not records:
        raise RuntimeError("No data found. Run the three framework experiments first.")

    ax.set_xlabel("Training Step")
    metric_title = args.metric.replace("_", " ").title()
    y_label = "Rate"
    ax.set_ylabel(f"{metric_title} ({y_label})")
    ax.set_title(f"Geometry Learning Curves by Framework ({metric_title})")
    ax.set_ylim(0.0, 1.0)
    ax.grid(alpha=0.3)
    ax.legend()

    out_plot = Path(args.output_plot)
    out_plot = out_plot if out_plot.is_absolute() else root / out_plot
    fig.tight_layout()
    fig.savefig(out_plot)

    out_csv = Path(args.output_csv)
    out_csv = out_csv if out_csv.is_absolute() else root / out_csv
    write_aggregated_csv(out_csv, records)

    print(f"Wrote aggregated CSV: {out_csv}")
    print(f"Wrote plot: {out_plot}")


if __name__ == "__main__":
    main()
