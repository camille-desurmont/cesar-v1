import os
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from runtime.inference.load_artifact import load_artifact_from_path, ArtifactNotFoundError
from runtime.inference.estimate_from_artifact import estimate_from_model, InvalidFeatureError
from runtime.query.query_pipeline import run_query, QueryResult
from prediction_contract.request_schema import EstimateRequest
from prediction_contract.response_schema import EstimateResponse
from prediction_contract.contract_version import ContractVersion

app = FastAPI(title="CESAR Prediction API", version="0.1.0")

_UI_DIR = Path(__file__).parent.parent / "query_ui"
if _UI_DIR.exists():
    app.mount("/ui", StaticFiles(directory=_UI_DIR), name="ui")

# Load the model and contract once and reuse for every request. We cache in _loaded so we do not
# read from disk on each call. If CESAR_MODEL_PATH or CESAR_CONTRACT_PATH are missing, we return 503
# (service unavailable) so callers know the API is not ready yet.
_loaded: tuple[object, ContractVersion] | None = None


def get_artifact() -> tuple[object, ContractVersion]:
    global _loaded
    if _loaded is not None:
        return _loaded
    model_path = Path(os.environ.get("CESAR_MODEL_PATH", ""))
    contract_path = Path(os.environ.get("CESAR_CONTRACT_PATH", ""))
    if not model_path or not contract_path:
        raise HTTPException(status_code=503, detail="CESAR_MODEL_PATH and CESAR_CONTRACT_PATH must be set")
    try:
        _loaded = load_artifact_from_path(model_path, contract_path)
        return _loaded
    except ArtifactNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_UI_DIR / "index.html")


class QueryRequest(BaseModel):
    query: str


@app.post("/query/", response_model=QueryResult)
def post_query(request: QueryRequest) -> QueryResult:
    data_csv = Path(os.environ.get("CESAR_DATA_CSV", "data/dvf_75015_all_years.csv"))
    if not data_csv.exists():
        raise HTTPException(status_code=503, detail=f"Data CSV not found: {data_csv}")

    model_path_str = os.environ.get("CESAR_MODEL_PATH", "")
    contract_path_str = os.environ.get("CESAR_CONTRACT_PATH", "")
    model_path = Path(model_path_str) if model_path_str else None
    contract_path = Path(contract_path_str) if contract_path_str else None

    try:
        return run_query(request.query, data_csv, model_path, contract_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/estimate/", response_model=EstimateResponse)
def post_estimate(
    request: EstimateRequest,
    artifact: Annotated[tuple[object, ContractVersion], Depends(get_artifact)],
) -> EstimateResponse:
    model, contract = artifact
    try:
        return estimate_from_model(model, request, contract)
    except InvalidFeatureError as e:
        raise HTTPException(status_code=422, detail=str(e))
