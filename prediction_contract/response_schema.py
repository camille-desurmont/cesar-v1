from typing import Optional

from pydantic import BaseModel, Field


# Response schema is the API contract for clients: they know exactly which fields to expect and
# their types. Adding optional fields (e.g. value_low_eur) with default None keeps backward
# compatibility: old clients ignore them, new clients can use them.
class EstimateResponse(BaseModel):
    estimated_value_eur: float = Field(..., description="Estimated value in euros")

    # Ideas: add value_low_eur, value_high_eur for confidence intervals (e.g. quantile regression).
    value_low_eur: Optional[float] = Field(None, description="Lower bound (optional)")
    value_high_eur: Optional[float] = Field(None, description="Upper bound (optional)")
