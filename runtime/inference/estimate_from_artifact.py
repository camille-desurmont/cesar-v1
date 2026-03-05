from typing import Any

import numpy as np

from prediction_contract.request_schema import EstimateRequest
from prediction_contract.response_schema import EstimateResponse
from prediction_contract.contract_version import ContractVersion


# Raising a dedicated exception for invalid features lets the API return 422 and the CLI print a
# clear message instead of a generic traceback. The contract defines the allowed type_local
# categories; we must use the same order for one-hot encoding as in training.
class InvalidFeatureError(Exception):
    pass


def _code_departement_to_numeric(code: str) -> float:
    s = str(code).strip()
    if s == "2A":
        return 20.0
    if s == "2B":
        return 21.0
    try:
        return float(int(s))
    except ValueError:
        return 0.0


def request_to_feature_row(request: EstimateRequest, contract: ContractVersion) -> np.ndarray:
    categories = contract.type_local_categories
    if request.type_local not in categories:
        raise InvalidFeatureError(f"type_local must be one of {categories}, got {request.type_local!r}")

    dept_num = _code_departement_to_numeric(request.code_departement)
    type_one_hot = [1.0 if c == request.type_local else 0.0 for c in categories]

    ordered = [
        float(request.surface_reelle_bati),
        float(request.nombre_pieces_principales),
        dept_num,
        *type_one_hot,
    ]
    return np.array(ordered, dtype=np.float64).reshape(1, -1)


def estimate_from_model(model: Any, request: EstimateRequest, contract: ContractVersion) -> EstimateResponse:
    X = request_to_feature_row(request, contract)
    pred = model.predict(X)
    value = float(pred.flat[0])
    return EstimateResponse(estimated_value_eur=value)
