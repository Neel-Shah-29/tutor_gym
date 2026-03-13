#!/usr/bin/env python3
"""Aggregate raw DataShop logs from the three-framework geometry experiments."""

from __future__ import annotations

import argparse
import csv
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


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description="Aggregate geometry logs from all 3 frameworks.")
    parser.add_argument(
        "--log-root-dir",
        default=str(script_dir / "log_al_3_frameworks"),
        help="Root folder containing feedback_only, nl_hint_only, feedback_and_nl_hint subfolders.",
    )
    parser.add_argument(
        "--output-csv",
        default=str(script_dir / "geometry_log_al_3_frameworks_aggregated.csv"),
        help="Output aggregated CSV path.",
    )
    parser.add_argument(
        "--output-tsv",
        default=str(script_dir / "geometry_log_al_3_frameworks_aggregated.txt"),
        help="Output aggregated TSV path.",
    )
    args = parser.parse_args()

    log_root_dir = Path(args.log_root_dir).resolve()
    output_csv = Path(args.output_csv).resolve()
    output_tsv = Path(args.output_tsv).resolve()

    rows: List[Dict[str, str]] = []
    base_fieldnames: List[str] | None = None
    total_files = 0

    for framework_name, subdir in FRAMEWORK_SUBDIRS:
        framework_dir = log_root_dir / subdir
        if not framework_dir.exists():
            continue
        log_files = sorted(framework_dir.glob("*.txt"))
        total_files += len(log_files)
        for log_file in log_files:
            for row in iter_rows(log_file):
                if base_fieldnames is None:
                    base_fieldnames = list(row.keys())
                row["Training Framework"] = framework_name
                row["Source Log File"] = log_file.name
                rows.append(row)

    if not rows or base_fieldnames is None:
        raise RuntimeError(f"No transaction rows found under {log_root_dir}")

    fieldnames = [*base_fieldnames, "Training Framework", "Source Log File"]
    write_rows(output_csv, rows, fieldnames, delimiter=",")
    write_rows(output_tsv, rows, fieldnames, delimiter="\t")

    print(f"Aggregated {len(rows)} rows from {total_files} files.")
    print(f"CSV: {output_csv}")
    print(f"TSV: {output_tsv}")


if __name__ == "__main__":
    main()
