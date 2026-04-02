# CESAR – CentraleSupelec-ESSEC System for Asset Rating

CESAR is a modular system to manage the lifecycle of a property valuation model and its uses: **batch prediction** (CSV in/out), **single-record prediction** (CLI), **HTTP API** (FastAPI), **acceptance tests** against the API, **version comparison** of two APIs, and a minimal **web UI**. 

---

## Goal

- **Goal:** Estimate the value of a property (e.g. `valeur_fonciere`) from a small set of features (surface, number of rooms, department, property type).
- **Uses:** (1) CLI: CSV → estimates → CSV or one record → one estimate. (2) API: POST `/estimate/` with JSON. (3) UI: form + map to input parameters and display the estimate.

---

## Source data

You can use data from DVF:
https://app.dvf.etalab.gouv.fr/ (new version at: https://explore.data.gouv.fr/fr/immobilier)

You may also use additional data from other sources, including synthetic (fake) data.
---

## How to run

### Prerequisites

- Python 3.11+
- Node 20+ (for the UI)

### 1. Install

Dependencies are declared in `pyproject.toml` (the modern replacement for `requirements.txt`). Use `pip install -e .` so the package is installed in editable mode: code changes are picked up without reinstalling.

```bash
pip install -e .
cd runtime/rating_ui && npm ci
```

### 2. Download data

DVF data files are not stored in the repository. Download them before training:

```bash
python data/download_dvf_paris.py
```

This downloads Paris property transaction data (2020–2024) from data.gouv.fr and saves one CSV per arrondissement in `data/`. The default data file used by the query CLI is `data/dvf_75015_all_years.csv` (Paris 15th), which is included in this download.

### 3. Train

**Simple way (recommended):** Put your CSV file(s) in the `data/` folder. Each CSV must have the same columns and at least: `surface_reelle_bati`, `nombre_pieces_principales`, `code_departement`, `type_local`, `valeur_fonciere`. Then:

```bash
python -m training.scripts.train_from_minimal_csv
```

The script loads every `*.csv` in `data/`, checks that all files have the same columns (and the required ones), combines the rows, and trains one model. If a file has missing or different columns, it raises a clear error.

**Single file (advanced):** To train from one CSV at a custom path, use `train_from_csv_and_export(csv_path, artifact_dir, ...)` from `training.asset_rating_model.train_and_export`.

This writes `artifact_storage/model_<version>.joblib` and `artifact_storage/contract_<version>.json`. Symlink or set `CESAR_MODEL_PATH` and `CESAR_CONTRACT_PATH` to these files.

### 4. Batch CLI

```bash
export CESAR_MODEL_PATH=artifact_storage/model_20250101120000.joblib
export CESAR_CONTRACT_PATH=artifact_storage/contract_20250101120000.json
cesar batch run --input input.csv --output output.csv
```

### 5. Single-record CLI

```bash
cesar predict-one run --surface 50 --pieces 3 --departement 75 --type Appartement
# From JSON file: cesar predict-one run --json one_record.json
# JSON output:  cesar predict-one run --surface 50 --pieces 3 --departement 75 --type Appartement --json-out
```

Use `--model` / `--contract` or set `CESAR_MODEL_PATH` and `CESAR_CONTRACT_PATH`. Valid `--type` values: `Appartement`, `Maison`, `Dépendance`, `Local industriel. commercial ou assimilé`.

### 6. API

```bash
uvicorn runtime.prediction_api.app:app --reload --host 0.0.0.0 --port 8000
```

Set `CESAR_MODEL_PATH` and `CESAR_CONTRACT_PATH` in the environment.

### 7. UI

```bash
cd runtime/rating_ui && npm run dev
```

Open the dev URL (e.g. http://localhost:5173). Set `window.CESAR_API_BASE = 'http://localhost:8000'` in the browser console if the API is on another origin.

### 8. Acceptance tests

Test cases are defined in Python in `model_acceptance_tests/test_cases.py`. Edit that file to add or change cases. With the API running:

```bash
export CESAR_API_URL=http://localhost:8000
cesar acceptance-tests run
```

### 9. Version comparison

Use `comparison.api_version_comparison.run_comparison` with a `CompareConfig` (two base URLs and a list of inputs). Ideas: implement diff of `estimated_value_eur`, regression criteria, or a report.

### 10. Experiment tracking (simple)

When you train often (different data, parameters, or ideas), it’s easy to forget what you did and which model version was best. **Experiment tracking** means: write down each run (when, what you used, what you got) in one place so you can compare later.

We provide a minimal version: no extra service, no database. One CSV file (e.g. `experiment_runs/runs.csv`) stores one row per training run. You can open it in Excel or read it in Python.

**What to record per run**

- **When** you ran (timestamp).
- **Which model version** was produced (e.g. the version string you wrote to `artifact_storage`).
- **What you used**: e.g. number of training rows, path to the CSV, or a short note (“first DVF subset”, “added feature X”).
- **What you got** (optional): e.g. a metric like mean absolute error on a fixed test set.

**How to use it**

After you train and export a model, call the logger once:

```python
from pathlib import Path
from training.asset_rating_model.train_and_export import train_from_csv_and_export
from training.experiment_log import log_run

csv_path = Path("path/to/dvf_subset.csv")
artifact_dir = Path("artifact_storage")
model_path, contract_path = train_from_csv_and_export(csv_path, artifact_dir)
# Version is in the filename, e.g. model_20250101120000.joblib
version = model_path.stem.replace("model_", "")

log_run(version, train_rows=1000, notes="DVF subset 75")  # use len(df) if you have the dataframe
```

If you compute a metric (e.g. test MAE), pass it as `metrics={"mae": 12000}`. To see past runs: `list_runs()` returns a list of dicts; or open `experiment_runs/runs.csv` in Excel.

**Why this helps**

- You can see which run used which data or settings.
- You can compare metrics across runs and pick the best model version to deploy.
- Later you can switch to a real experiment tracker (e.g. MLflow) that adds plots, parameters, and artifacts; the idea is the same: record what you did and what you got.

---

## Ideas to implement

Organized by **difficulty / scope** (from small to larger).

1. **Easier**
   - Add more acceptance test cases in `model_acceptance_tests/test_cases.py`; optional property-based tests.
   - UI: improve map (e.g. click on department to set `code_departement`); display value range if the API returns `value_low_eur` / `value_high_eur`.
   - Confidence intervals: in `estimate_from_artifact` and the API response, add optional `value_low_eur` / `value_high_eur` (e.g. quantile regression).

2. **Medium**
   - Complete the API version comparison: diff responses, define regression criteria, output a small report (HTML or JSON).
   - CI/CD: e.g. GitHub Actions to run acceptance tests on every push.

3. **Larger**
   - Authentication/authorization on the API.
   - Model registry (e.g. MLflow) instead of a single artifact directory.
   - Database or logging for requests / A/B tests.

---

## Repository layout

Code is grouped by MLOps phase so students can navigate easily.

- **Root:** `prediction_contract/` – shared request/response and on-disk contract (feature names, version). `cli/` – all CLI commands (typer); entrypoint: `cesar`. Logic for each command lives in the matching folder (e.g. `runtime/`, `model_acceptance_tests/`).
- **runtime/** – serving: `prediction_api/` (FastAPI), `batch_prediction/` (read CSV, run estimates, write CSV), `inference/` (load artifact, estimate from model), `rating_ui/` (form, map of France).
- **training/** – `asset_rating_model/` (train and export), `scripts/` (e.g. minimal CSV demo), `experiment_log.py` (simple run logging to a CSV).
- **model_acceptance_tests/** – hardcoded test cases in Python, runner; CLI is in `cli/acceptance_tests.py`.
- **comparison/** – `api_version_comparison/` (config and stub to compare two APIs).
- **artifact_storage/** – directory for model and contract (versioned names); created on first train.

---

## Project ideas for students

Here are concrete ways to extend CESAR. All are doable in a short course; pick one or combine a few depending on your time and interests.

**More and better data**
- Add extra CSVs to `data/` (e.g. other DVF extracts, open data from data.gouv.fr) and retrain. Compare experiment-log metrics across runs to see if more data helps.
- Enrich the training CSV with one new column (e.g. `code_postal` or distance to a city center from open data), add it to the contract and model, and measure the impact. Good way to see the full pipeline: data → training → contract → API.

**Expose the model via MCP (Model Context Protocol)**
- Build a small MCP server that exposes a “get property estimate” tool. Other apps (or an AI assistant in Cursor/Claude) can then call your model without touching the API directly. Great for “my model as a building block” and learning how tools are exposed to LLMs.
- Start from the existing inference code: one function that takes (surface, rooms, department, type) and returns the estimate. Wrap it in an MCP server that declares one tool and calls that function. The MCP docs and examples are minimal; you mainly need to return JSON in the right shape.

**Smarter UI**
- Make the map clickable: click a department on the Leaflet map to set `code_departement` in the form. You only need to add a GeoJSON layer (e.g. French departments) and a click handler that updates the form.
- Show the value range when the API returns `value_low_eur` / `value_high_eur` (if you add confidence intervals to the model). The UI already has a placeholder for “Range”.

**Anomaly detection (“why so cheap / so expensive?”)**
- Add a feature that flags surprising estimates: “This estimate looks unusually high (or low) for the given surface, location, and type.” Users get a nudge to double-check or add more context. There are several ways to implement it; the simplest use the model’s own uncertainty.
- **Option A – Confidence ranges:** If the model outputs a range (`value_low_eur`, `value_high_eur`), you can treat a very wide range as “uncertain” and show a warning, or compare the point estimate to the range (e.g. if the user’s prior belief is outside the range, flag it). Implementing ranges may require changing the model (e.g. quantile regression or prediction intervals) and the contract; the response schema already has optional `value_low_eur` / `value_high_eur`.
- **Option B – Simple rules:** Without changing the model, you can add heuristics (e.g. “price per m² far above/below the department average” using training or external stats) and return a flag in the API (e.g. `anomaly_warning: "high_for_department"`). Good first step before touching the model.
- **Option C – Second model or score:** Train a small classifier or scorer that predicts “is this estimate suspicious?” from the same inputs plus the model’s point estimate (e.g. residual-style or comparison to a baseline). The API then returns both the estimate and a binary or score for “possible anomaly”.

Pick one option and plug it into the API and (optionally) the UI; even a simple rule or a wide-range check makes the system more interpretable.

**API and developer experience**
- Add a `/health` that checks that the model and contract load (e.g. read one file). Helps deployment and monitoring.
- Add one extra endpoint, e.g. GET `/model_info`, that returns the contract version and feature names. Useful for scripts or the UI to show “which model is running”.

**Deployment and ops**
- Add a simple GitHub Action that runs acceptance tests on every push. One YAML file that installs deps, starts the API (with a test model), and runs `cesar acceptance-tests run`.

**Combining ideas**
- “Data + experiment log”: train on two different data mixes, log each run with `experiment_log`, then compare which version the acceptance tests prefer.
- “MCP + UI”: build the MCP server, then use it from a small script or from Cursor’s MCP client to get estimates; keep the existing UI for demos.
- “API + CI”: add `/health` and `/model_info`, then add a GitHub Action that checks the API is healthy before running acceptance tests.

Pick something that excites you and fits your timeline; even one of these will deepen your understanding of the stack.
