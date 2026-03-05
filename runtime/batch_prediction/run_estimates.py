from typing import Any

import numpy as np
import pandas as pd

from prediction_contract.feature_schema import TYPE_LOCAL_CATEGORIES
from runtime.inference.estimate_from_artifact import request_to_feature_row
from prediction_contract.contract_version import ContractVersion
from prediction_contract.request_schema import EstimateRequest


# We reuse request_to_feature_row so batch and single-record paths use identical feature encoding.
# Defaulting unknown type_local to "Appartement" avoids failing the whole batch for one bad row;
# in production you might instead log a warning and skip the row or use a dedicated "Unknown" category.
def _row_to_request(row: pd.Series) -> EstimateRequest:
    type_local = str(row["type_local"]).strip()
    if type_local not in TYPE_LOCAL_CATEGORIES:
        type_local = "Appartement"
    return EstimateRequest(
        surface_reelle_bati=float(row["surface_reelle_bati"]) if pd.notna(row["surface_reelle_bati"]) else 0.0,
        nombre_pieces_principales=float(row["nombre_pieces_principales"]) if pd.notna(row["nombre_pieces_principales"]) else 0.0,
        code_departement=str(row["code_departement"]).strip()[:3],
        type_local=type_local,
    )


def run_estimates_on_dataframe(
    df: pd.DataFrame,
    model: Any,
    contract: ContractVersion,
) -> np.ndarray:
    preds: list[float] = []
    for _, row in df.iterrows():
        req = _row_to_request(row)
        X = request_to_feature_row(req, contract)
        pred = model.predict(X)
        preds.append(float(pred.flat[0]))
    return np.array(preds)
