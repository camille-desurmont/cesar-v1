"""Acceptance test cases: each case represents one request to the model and the expected response.

Add or edit cases below to test different inputs. Each case has:
  - name: short label (e.g. "Paris apartment 50m2 3 rooms")
  - input: the four fields the API expects (surface, rooms, department, type)
  - expected_value_eur: optional; if set, the API response must be close to this value
  - expected_status: optional; if set, the API must return this HTTP status (e.g. 422 for validation errors)
"""

from model_acceptance_tests.test_case_schema import TestCase, TestCaseInput

# Case 1: Paris apartment, 50 m², 3 rooms
case_paris_apartment = TestCase(
    name="Paris apartment 50m2 3 rooms",
    input=TestCaseInput(
        surface_reelle_bati=50.0,
        nombre_pieces_principales=3.0,
        code_departement="75",
        type_local="Appartement",
    ),
)

# Case 2: House in Rhône, 100 m², 5 rooms
case_house_rhone = TestCase(
    name="House 100m2 5 rooms",
    input=TestCaseInput(
        surface_reelle_bati=100.0,
        nombre_pieces_principales=5.0,
        code_departement="69",
        type_local="Maison",
    ),
)

ACCEPTANCE_TEST_CASES = [
    case_paris_apartment,
    case_house_rhone,
]
