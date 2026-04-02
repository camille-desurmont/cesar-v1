# Comparing two API versions (e.g. old prod vs new candidate) before a release helps catch
# regressions: same inputs should yield similar or acceptable outputs. This module calls both
# endpoints and returns side-by-side results; you can extend it with tolerance checks, summary
# stats, or a report. Ideas: implement actual diff of estimated_value_eur, regression criteria,
# or a small HTML/JSON report for review.

from typing import Any

import httpx

from comparison.api_version_comparison.compare_config_schema import CompareConfig


def fetch_estimate(base_url: str, payload: dict[str, Any], timeout: float = 10.0) -> tuple[int, dict[str, Any]]:
    with httpx.Client(timeout=timeout) as client:
        response = client.post(f"{base_url.rstrip('/')}/estimate/", json=payload)
    try:
        data = response.json()
    except Exception:
        data = {}
    return response.status_code, data


def run_comparison(config: CompareConfig, timeout: float = 10.0) -> list[dict[str, Any]]:
    """Call both APIs for each input; return list of {input_index, status_a, status_b, body_a, body_b}."""
    results: list[dict[str, Any]] = []
    for i, inp in enumerate(config.inputs):
        payload = inp.model_dump()
        status_a, body_a = fetch_estimate(config.base_url_a, payload, timeout=timeout)
        status_b, body_b = fetch_estimate(config.base_url_b, payload, timeout=timeout)
        results.append({
            "input_index": i,
            "status_a": status_a,
            "status_b": status_b,
            "body_a": body_a,
            "body_b": body_b,
        })
    return results
