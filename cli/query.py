"""CLI command: query apartments using natural language.

The real work lives in runtime.query. This file only defines the CLI.
"""

import json
import os
from pathlib import Path

import typer

from runtime.query.query_pipeline import run_query


query_app = typer.Typer(help="Query apartments using natural language.")


@query_app.command("run")
def run_query_cmd(
    query: str = typer.Argument(..., help="Natural language query (e.g. '3-room apartment under 500k')"),
    data_csv: Path = typer.Option(
        None, "--data", "-d", path_type=Path,
        help="Path to data CSV (default: CESAR_DATA_CSV or data/dvf_75115_000CM.csv)",
    ),
    model_path: Path | None = typer.Option(None, "--model", "-m", path_type=Path),
    contract_path: Path | None = typer.Option(None, "--contract", "-c", path_type=Path),
    json_out: bool = typer.Option(False, "--json-out", help="Output as JSON"),
) -> None:
    """Search for apartments matching a natural language description."""
    # Resolve data CSV path
    if data_csv is None:
        data_csv = Path(os.environ.get("CESAR_DATA_CSV", "data/dvf_75115_000CM.csv"))
    if not data_csv.exists():
        typer.echo(f"Error: Data CSV not found: {data_csv}", err=True)
        raise typer.Exit(1)

    # Resolve model/contract paths (optional)
    if model_path is None:
        env_model = os.environ.get("CESAR_MODEL_PATH")
        if env_model:
            model_path = Path(env_model)
    if contract_path is None:
        env_contract = os.environ.get("CESAR_CONTRACT_PATH")
        if env_contract:
            contract_path = Path(env_contract)

    try:
        result = run_query(query, data_csv, model_path, contract_path)
    except RuntimeError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    if json_out:
        typer.echo(result.model_dump_json(indent=2))
    else:
        typer.echo(f"\nQuery: {result.query}")
        typer.echo(f"Parsed filters: {result.parsed_criteria.model_dump(exclude_none=True)}")
        typer.echo(f"Found {result.total_matches} matching properties:\n")

        for i, match in enumerate(result.matches, 1):
            typer.echo(f"  {i}. {match.adresse} ({match.code_postal})")
            typer.echo(f"     Type: {match.type_local}")
            if match.surface_m2:
                typer.echo(f"     Surface: {match.surface_m2} m²")
            if match.rooms:
                typer.echo(f"     Rooms: {match.rooms}")
            if match.actual_price_eur:
                typer.echo(f"     Actual price: €{match.actual_price_eur:,.0f}")
            if match.estimated_price_eur:
                typer.echo(f"     ML estimate:  €{match.estimated_price_eur:,.0f}")
            typer.echo(f"     Date: {match.date_mutation}")
            typer.echo()