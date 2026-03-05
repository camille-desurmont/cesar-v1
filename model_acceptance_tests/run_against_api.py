"""Run acceptance test cases against the live API (HTTP)."""

import httpx

from model_acceptance_tests.test_case_schema import TestCase


def run_one_case(
    base_url: str,
    case: TestCase,
    timeout: float = 10.0,
) -> tuple[bool, str]:
    """Run one test case against POST /estimate/. Return (passed, message)."""
    payload = case.input.model_dump()
    with httpx.Client(timeout=timeout) as client:
        response = client.post(f"{base_url.rstrip('/')}/estimate/", json=payload)
    if case.expected_status is not None:
        if response.status_code != case.expected_status:
            return False, f"Expected status {case.expected_status}, got {response.status_code}"
        return True, "ok"
    if response.status_code != 200:
        return False, f"Status {response.status_code}: {response.text}"
    data = response.json()
    value = data.get("estimated_value_eur")
    if value is None:
        return False, "Response missing estimated_value_eur"
    if case.expected_value_eur is not None:
        tol = 0.01 * abs(case.expected_value_eur) or 1.0
        if abs(value - case.expected_value_eur) > tol:
            return False, f"Expected ~{case.expected_value_eur}, got {value}"
    return True, "ok"


def run_all_cases(
    base_url: str,
    cases: list[TestCase],
    timeout: float = 10.0,
) -> list[tuple[str, bool, str]]:
    """Run all cases; return list of (name, passed, message)."""
    results: list[tuple[str, bool, str]] = []
    for case in cases:
        passed, msg = run_one_case(base_url, case, timeout=timeout)
        results.append((case.name, passed, msg))
    return results
