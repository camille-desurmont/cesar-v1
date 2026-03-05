from typing import Any

from pydantic import BaseModel, Field


# The contract file is saved next to the model and describes exactly which features the model
# expects and in what order. This avoids "training used columns A,B,C but serving sent B,A,D":
# API, CLI, and batch all read the same contract so behavior stays consistent. Versioning the
# contract (e.g. in the filename) lets you pin a deployment to a specific model version.
class ContractVersion(BaseModel):

    model_version: str = Field(..., description="Model version (e.g. timestamp or semver)")
    feature_names: list[str] = Field(..., min_length=1, description="Feature names in expected order")
    target_name: str = Field(..., description="Target column name (e.g. valeur_fonciere)")
    type_local_categories: list[str] = Field(..., description="Categories for type_local (one-hot or ordinal)")

    def to_serializable(self) -> dict[str, Any]:
        return self.model_dump()

    @classmethod
    def from_serializable(cls, data: dict[str, Any]) -> "ContractVersion":
        return cls.model_validate(data)
