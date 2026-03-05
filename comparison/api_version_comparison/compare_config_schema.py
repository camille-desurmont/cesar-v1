from typing import Any

from pydantic import BaseModel, Field

from model_acceptance_tests.test_case_schema import TestCaseInput


class CompareConfig(BaseModel):
    """Config for comparing two API versions: base URLs and list of inputs to send."""

    base_url_a: str = Field(..., description="First API base URL (e.g. current prod)")
    base_url_b: str = Field(..., description="Second API base URL (e.g. candidate)")
    inputs: list[TestCaseInput] = Field(..., min_length=1, description="Inputs to send to both APIs")
