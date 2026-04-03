# CESAR – CentraleSupelec-ESSEC System for Asset Rating

CESAR estimates the value of a Paris property from a small set of features (surface, number of rooms, arrondissement, property type) using a machine learning model trained on DVF transaction data.

---

## Install

```bash
pip install -e .
```

Dependencies (declared in `pyproject.toml`):

| Package | Role |
|---|---|
| `scikit-learn` | ML model training and inference |
| `pandas` | Data loading and filtering |
| `joblib` | Model serialization |
| `pydantic` | Request/response schema validation |
| `fastapi` + `uvicorn` | HTTP prediction API |
| `typer` | CLI commands |
| `anthropic` | LLM-based natural language query parser |
| `httpx` | HTTP client for acceptance tests |

---

## Download data

DVF data files are not stored in the repository. Download them before training:

```bash
python data/download_dvf_paris.py
```

This script downloads Paris property transaction data (2020–2024) from `data.gouv.fr` and saves one CSV per arrondissement in `data/` (e.g. `data/dvf_75015_all_years.csv`).

Options:
```bash
python data/download_dvf_paris.py --years 2023 2024
python data/download_dvf_paris.py --years 2023 --arrondissements 75001 75002
```

---

## ML prediction: natural language query

The main feature is a natural language query interface that searches real DVF transactions and, when a trained model is available, enriches results with ML price estimates.

```bash
cesar query run "3-room apartment under 500k" --model artifact_storage/model_<version>.joblib --contract artifact_storage/contract_<version>.json
```

**Pipeline** (`runtime/query/query_pipeline.py`):
1. The user's query is parsed by an LLM into structured filters (`surface`, `rooms`, `price`, etc.).
2. The DVF CSV is loaded and filtered against those criteria.
3. For each matching property, the ML model produces a price estimate from `surface_reelle_bati`, `nombre_pieces_principales`, `code_departement`, and `type_local`.
4. Undervaluation signals are computed and attached to each result.

The model and contract paths can also be set via environment variables:
```bash
export CESAR_MODEL_PATH=artifact_storage/model_<version>.joblib
export CESAR_CONTRACT_PATH=artifact_storage/contract_<version>.json
export CESAR_DATA_CSV=data/dvf_75015_all_years.csv
```

### Undervaluation detection

For each result that has both an actual transaction price and an ML estimate, `flag_undervalued` (`runtime/query/undervaluation.py`) computes:

- **`discount_pct`** – how much cheaper the actual price is relative to the ML estimate: `(estimate − actual) / estimate × 100`. Positive = potential deal.
- **`is_undervalued`** – `True` when `discount_pct ≥ 20%` (configurable via `threshold_pct`).
- **`value_rank`** – rank among all scored results (1 = best deal).

Properties where either price is missing are left unscored.

---

## Model limits

- **Geography:** trained only on Paris (department 75). Estimates for other departments will be unreliable.
- **Features:** only four inputs — surface, rooms, department, property type. Location within Paris (arrondissement, street) is not used.
- **Data range:** DVF data covers 2020–2024. The model does not account for market drift after the training period.
- **Property types:** only `Appartement`, `Maison`, `Dépendance`, `Local industriel. commercial ou assimilé`.
- **Undervaluation signal:** the gap between actual transaction price and ML estimate reflects model error as much as a true deal — it should not be taken as financial advice.
