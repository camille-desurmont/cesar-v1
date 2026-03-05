"""CLI command: run acceptance tests against the API.

The real work (test cases, HTTP calls, pass/fail) lives in model_acceptance_tests.
This file only defines the command-line interface (typer).
"""

import os

import typer

from model_acceptance_tests.test_cases import ACCEPTANCE_TEST_CASES
from model_acceptance_tests.run_against_api import run_all_cases

acceptance_tests_app = typer.Typer(
    name="acceptance-tests",
    help="Run acceptance tests against the CESAR API.",
)


@acceptance_tests_app.command("run")
def run_acceptance_tests(
    base_url: str = typer.Option(
        None,
        "--base-url",
        "-u",
        help="API base URL (or set CESAR_API_URL)",
    ),
) -> None:
    """Run all test cases and print pass/fail for each."""
    url = base_url or os.environ.get("CESAR_API_URL", "http://localhost:8000")
    results = run_all_cases(url, ACCEPTANCE_TEST_CASES)

    failed_count = 0
    for name, passed, msg in results:
        status = "PASS" if passed else "FAIL"
        typer.echo(f"  [{status}] {name}: {msg}")
        if not passed:
            failed_count += 1

    if failed_count > 0:
        typer.echo(f"\n{failed_count} failed, {len(results) - failed_count} passed.")
        raise typer.Exit(1)
    typer.echo(f"\nAll {len(results)} passed.")
