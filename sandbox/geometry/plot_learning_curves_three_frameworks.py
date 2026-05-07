#!/usr/bin/env python3
"""Plot geometry learning curves for all three frameworks.

By default, log files within each framework are concatenated in file order to
reproduce the original plotting behavior. A mean-across-runs mode is available
when per-run aggregation is needed.
"""

from __future__ import annotations

import argparse
import csv
import math
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


def load_run_curves(log_dir: Path, metric: str) -> List[Dict[str, object]]:
    run_curves: List[Dict[str, object]] = []
    for log_file in sorted(log_dir.glob("*.txt")):
        rows = list(iter_rows(log_file))
        if not rows:
            continue
        steps, values, count_hist = build_learning_curve(rows, metric)
        if not steps:
            continue
        run_curves.append(
            {
                "source_log_file": log_file.name,
                "steps": steps,
                "values": values,
                "count_hist": count_hist,
            }
        )
    return run_curves


def sample_stddev(values: List[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / (len(values) - 1)
    return math.sqrt(variance)


def aggregate_run_curves(run_curves: List[Dict[str, object]]) -> tuple[List[int], List[float], List[Dict[str, object]]]:
    max_len = max(len(run_curve["values"]) for run_curve in run_curves)
    steps: List[int] = []
    mean_values: List[float] = []
    stats: List[Dict[str, object]] = []

    for index in range(max_len):
        step = index + 1
        step_values = [
            run_curve["values"][index]
            for run_curve in run_curves
            if index < len(run_curve["values"])
        ]
        if not step_values:
            continue

        mean_value = sum(step_values) / len(step_values)
        std_value = sample_stddev(step_values)
        sem_value = std_value / math.sqrt(len(step_values)) if step_values else 0.0

        steps.append(step)
        mean_values.append(mean_value)
        stats.append(
            {
                "step": step,
                "mean_value": mean_value,
                "std_value": std_value,
                "sem_value": sem_value,
                "n_runs": len(step_values),
            }
        )

    return steps, mean_values, stats


def write_records_csv(path: Path, records: List[Dict[str, object]]) -> None:
    if not records:
        return
    columns = list(records[0].keys())
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
    parser.add_argument(
        "--aggregation-mode",
        default="concat",
        choices=["mean_across_runs", "concat"],
        help="How to combine multiple log files per framework.",
    )
    parser.add_argument(
        "--variability-band",
        default="sem",
        choices=["none", "sem", "std"],
        help="Band to draw around the mean curve in mean_across_runs mode.",
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

        run_curves = load_run_curves(log_dir, args.metric)
        if not run_curves:
            print(f"No rows found in {log_dir}")
            continue

        if args.aggregation_mode == "concat":
            steps, values, count_hist = build_learning_curve(iter_log_rows(log_dir), args.metric)
            if not steps:
                continue
            final_counts = count_hist[-1]
            ax.plot(steps, values, label=f"{framework} (rows={final_counts['total']})")
            for step_idx, value, counts in zip(steps, values, count_hist):
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
                        "aggregation_mode": args.aggregation_mode,
                    }
                )
            continue

        steps, mean_values, stats = aggregate_run_curves(run_curves)
        if not steps:
            continue

        line, = ax.plot(steps, mean_values, label=f"{framework} (runs={len(run_curves)})")
        if args.variability_band != "none":
            band_key = "sem_value" if args.variability_band == "sem" else "std_value"
            lower = [max(0.0, stat["mean_value"] - stat[band_key]) for stat in stats]
            upper = [min(1.0, stat["mean_value"] + stat[band_key]) for stat in stats]
            ax.fill_between(steps, lower, upper, color=line.get_color(), alpha=0.18)

        for stat in stats:
            records.append(
                {
                    "framework": framework,
                    "step": stat["step"],
                    "mean_value": stat["mean_value"],
                    "std_value": stat["std_value"],
                    "sem_value": stat["sem_value"],
                    "n_runs": stat["n_runs"],
                    "metric": args.metric,
                    "aggregation_mode": args.aggregation_mode,
                    "variability_band": args.variability_band,
                }
            )

    if not records:
        raise RuntimeError("No data found. Run the three framework experiments first.")

    ax.set_xlabel("Training Step")
    metric_title = args.metric.replace("_", " ").title()
    y_label = "Rate"
    ax.set_ylabel(f"{metric_title} ({y_label})")
    mode_title = "Mean Across Runs" if args.aggregation_mode == "mean_across_runs" else "Concatenated Logs"
    ax.set_title(f"Geometry Learning Curves by Framework ({metric_title}, {mode_title})")
    ax.set_ylim(0.0, 1.0)
    ax.grid(alpha=0.3)
    ax.legend()

    out_plot = Path(args.output_plot)
    out_plot = out_plot if out_plot.is_absolute() else root / out_plot
    fig.tight_layout()
    fig.savefig(out_plot)
    plt.close(fig)

    out_csv = Path(args.output_csv)
    out_csv = out_csv if out_csv.is_absolute() else root / out_csv
    write_records_csv(out_csv, records)

    print(f"Wrote aggregated CSV: {out_csv}")
    print(f"Wrote plot: {out_plot}")


if __name__ == "__main__":
    main()
