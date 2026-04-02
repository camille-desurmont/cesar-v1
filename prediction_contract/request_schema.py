from typing import Literal

from pydantic import BaseModel, Field

# Defining request shapes with Pydantic gives validation at the boundary (API, CLI, batch): invalid
# inputs are rejected early with clear errors, and type hints make the contract explicit for anyone
# reading or evolving the code. In production, never trust raw JSON or CSV without validation.

# Property types observed in DVF (subset used by default model).
# Ideas: extend with more types or make this configurable from contract.
TYPE_LOCAL_VALUES = Literal["Appartement", "Maison"]


class EstimateRequest(BaseModel):
    surface_reelle_bati: float = Field(..., ge=0, description="Living area in m²")
    nombre_pieces_principales: float = Field(..., ge=0, description="Number of main rooms")
    code_departement: str = Field(..., min_length=2, max_length=3, description="Department code (e.g. 75, 2A)")
    type_local: TYPE_LOCAL_VALUES = Field(..., description="Property type")


class EstimateRequestOptionalBounds(BaseModel):
    """Optional: for future value range / confidence interval support."""

    pass
