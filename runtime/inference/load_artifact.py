import json
from pathlib import Path
from typing import Any

import joblib

from prediction_contract.contract_version import ContractVersion


# Custom exceptions make error handling explicit: callers can catch ArtifactNotFoundError vs
# ContractInvalidError and decide what to do (e.g. return 503 vs 500). Prefer specific exceptions
# over generic ones so failures are easier to diagnose and handle in API or CLI.
class ArtifactNotFoundError(Exception):
    pass


class ContractInvalidError(Exception):
    pass


def load_contract(path: Path) -> ContractVersion:
    if not path.exists():
        raise ArtifactNotFoundError(f"Contract file not found: {path}")
    raw: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    return ContractVersion.from_serializable(raw)


def load_model(path: Path) -> Any:
    if not path.exists():
        raise ArtifactNotFoundError(f"Model file not found: {path}")
    return joblib.load(path)


def load_artifact_from_path(model_path: Path, contract_path: Path) -> tuple[Any, ContractVersion]:
    contract = load_contract(contract_path)
    model = load_model(model_path)
    return model, contract
