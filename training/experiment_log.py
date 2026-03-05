"""
Simple experiment tracking: write each training run to a CSV so you can see what you did and what you got.

No extra libraries, no server. Just one CSV file (e.g. experiment_runs/runs.csv) that you can open
in Excel or read in Python. Call log_run() after each training run; use list_runs() to see history.
"""

import csv
import json
from datetime import datetime
from pathlib import Path

# Where we store the log. Change this if you want (e.g. artifact_storage/runs.csv).
DEFAULT_LOG_DIR = Path("experiment_runs")
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "runs.csv"

# Column names in the CSV.
COLUMNS = ["timestamp", "model_version", "train_rows", "notes", "params", "metrics"]


def log_run(
    model_version: str,
    train_rows: int | None = None,
    notes: str = "",
    params: dict | None = None,
    metrics: dict | None = None,
    log_path: Path | None = None,
) -> None:
    """
    Append one row to the experiment log. Call this after you train and export a model.

    Example:
        log_run("20250101120000", train_rows=1000, notes="First run with DVF subset")
    """
    path = Path(log_path) if log_path else DEFAULT_LOG_FILE
    path.parent.mkdir(parents=True, exist_ok=True)

    row = {
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "model_version": model_version,
        "train_rows": str(train_rows) if train_rows is not None else "",
        "notes": notes or "",
        "params": json.dumps(params) if params else "",
        "metrics": json.dumps(metrics) if metrics else "",
    }

    file_exists = path.exists()
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


def list_runs(log_path: Path | None = None) -> list[dict]:
    """
    Read the log and return a list of runs (each run is a dict with keys like timestamp, model_version, train_rows, notes, params, metrics).
    If the file does not exist, returns an empty list.
    """
    path = Path(log_path) if log_path else DEFAULT_LOG_FILE
    if not path.exists():
        return []

    runs = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("params"):
                try:
                    row["params"] = json.loads(row["params"])
                except json.JSONDecodeError:
                    pass
            if row.get("metrics"):
                try:
                    row["metrics"] = json.loads(row["metrics"])
                except json.JSONDecodeError:
                    pass
            runs.append(row)
    return runs
