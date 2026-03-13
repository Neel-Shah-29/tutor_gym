#!/usr/bin/env python3
"""Aggregate DataShop transaction logs from log_al into one CSV/TSV file."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, Iterable, List


def iter_rows(log_file: Path) -> Iterable[Dict[str, str]]:
    with log_file.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            return

        for row in reader:
            if not row:
                continue
            if not any((value or "").strip() for value in row.values()):
                continue
            # Some logs contain an accidental repeated header row in the body.
            if all((row.get(key) or "").strip() == key for key in reader.fieldnames):
                continue
            yield {key: (row.get(key) or "") for key in reader.fieldnames}


def write_rows(path: Path, rows: List[Dict[str, str]], fieldnames: List[str], delimiter: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    workspace_root = Path(__file__).resolve().parents[3]
    default_log_dir = script_dir / "log_al"
    default_csv = workspace_root / "pyAFM" / "geometry_log_al_aggregated.csv"
    default_tsv = workspace_root / "pyAFM" / "geometry_log_al_aggregated.txt"

    parser = argparse.ArgumentParser(description="Aggregate tutor_gym geometry logs.")
    parser.add_argument(
        "--log-dir",
        default=str(default_log_dir),
        help="Directory containing per-run DataShop .txt files.",
    )
    parser.add_argument(
        "--output-csv",
        default=str(default_csv),
        help="Output CSV file path (comma-separated).",
    )
    parser.add_argument(
        "--output-tsv",
        default=str(default_tsv),
        help="Output TSV file path (tab-separated; directly usable with learning_curves.ipynb).",
    )
    args = parser.parse_args()

    log_dir = Path(args.log_dir).resolve()
    output_csv = Path(args.output_csv).resolve()
    output_tsv = Path(args.output_tsv).resolve()

    log_files = sorted(log_dir.glob("*.txt"))
    if not log_files:
        raise FileNotFoundError(f"No .txt logs found in {log_dir}")

    rows: List[Dict[str, str]] = []
    base_fieldnames: List[str] | None = None

    for log_file in log_files:
        for row in iter_rows(log_file):
            if base_fieldnames is None:
                base_fieldnames = list(row.keys())
            row["Source Log File"] = log_file.name
            rows.append(row)

    if not rows or base_fieldnames is None:
        raise RuntimeError(f"No transaction rows were read from {log_dir}")

    fieldnames = [*base_fieldnames, "Source Log File"]
    write_rows(output_csv, rows, fieldnames, delimiter=",")
    write_rows(output_tsv, rows, fieldnames, delimiter="\t")

    print(f"Aggregated {len(rows)} rows from {len(log_files)} files.")
    print(f"CSV: {output_csv}")
    print(f"TSV: {output_tsv}")


if __name__ == "__main__":
    main()
