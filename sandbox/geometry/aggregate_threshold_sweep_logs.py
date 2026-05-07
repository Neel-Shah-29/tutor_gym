#!/usr/bin/env python3
"""Aggregate geometry logs across predicate-threshold sweep runs."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path
from typing import Dict, Iterable, List


FRAMEWORK_SUBDIRS = (
    ("feedback_only", "feedback_only"),
    ("nl_hint_only", "nl_hint_only"),
    ("feedback_and_nl_hint", "feedback_and_nl_hint"),
)


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
            yield {key: (row.get(key) or "") for key in headers}


def write_rows(path: Path, rows: List[Dict[str, str]], fieldnames: List[str], delimiter: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def parse_source_metadata(log_file: Path, framework_name: str) -> Dict[str, str]:
    stem = log_file.stem
    metadata = {
        "Agent Index": "",
        "Agent Seed": "",
        "NL Hint Delivery": "",
        "Data Split": "train",
    }

    match = re.search(r"agent(\d+)_seed(\d+)", stem)
    if match:
        metadata["Agent Index"] = match.group(1)
        metadata["Agent Seed"] = match.group(2)

    framework_tag = f"_{framework_name}_"
    tail = stem.split(framework_tag, 1)[1] if framework_tag in stem else stem
    for delivery in ("off", "demo_only", "feedback_only", "demo_and_feedback"):
        if tail.startswith(f"{delivery}_") or f"_{delivery}_" in tail:
            metadata["NL Hint Delivery"] = delivery
            break

    return metadata


def parse_threshold_dir(path: Path) -> int:
    name = path.name
    if not name.startswith("threshold_"):
        raise ValueError(f"Unrecognized threshold directory name: {name}")
    return int(name.split("_", 1)[1])


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Aggregate geometry threshold-sweep logs.")
    parser.add_argument(
        "--log-root-dir",
        default=str(script_dir / "logs_predicate_threshold_experiments"),
        help="Root folder containing threshold_<N>/framework_subdir log files.",
    )
    parser.add_argument(
        "--output-csv",
        default=str(script_dir / "geometry_threshold_sweep_aggregated.csv"),
        help="Output aggregated CSV path.",
    )
    parser.add_argument(
        "--output-tsv",
        default=str(script_dir / "geometry_threshold_sweep_aggregated.txt"),
        help="Output aggregated TSV path.",
    )
    args = parser.parse_args()

    log_root_dir = Path(args.log_root_dir).resolve()
    output_csv = Path(args.output_csv).resolve()
    output_tsv = Path(args.output_tsv).resolve()

    threshold_dirs = sorted(
        [path for path in log_root_dir.iterdir() if path.is_dir() and path.name.startswith("threshold_")]
    )
    if not threshold_dirs:
        raise RuntimeError(f"No threshold_* directories found under {log_root_dir}")

    rows: List[Dict[str, str]] = []
    base_fieldnames: List[str] | None = None

    for threshold_dir in threshold_dirs:
        threshold = parse_threshold_dir(threshold_dir)
        for framework_name, subdir in FRAMEWORK_SUBDIRS:
            framework_dir = threshold_dir / subdir
            if not framework_dir.exists():
                continue
            for log_file in sorted(framework_dir.glob("*.txt")):
                for row in iter_rows(log_file):
                    if base_fieldnames is None:
                        base_fieldnames = list(row.keys())
                    row["Training Framework"] = framework_name
                    row["Predicate Threshold"] = str(threshold)
                    row["Source Log File"] = log_file.name
                    row.update(parse_source_metadata(log_file, framework_name))
                    rows.append(row)

    if not rows or base_fieldnames is None:
        raise RuntimeError(f"No transaction rows found under {log_root_dir}")

    fieldnames = [
        *base_fieldnames,
        "Training Framework",
        "Predicate Threshold",
        "Source Log File",
        "Agent Index",
        "Agent Seed",
        "NL Hint Delivery",
        "Data Split",
    ]
    write_rows(output_csv, rows, fieldnames, delimiter=",")
    write_rows(output_tsv, rows, fieldnames, delimiter="\t")

    print(f"Aggregated {len(rows)} rows from {len(threshold_dirs)} threshold settings.")
    print(f"CSV: {output_csv}")
    print(f"TSV: {output_tsv}")


if __name__ == "__main__":
    main()
