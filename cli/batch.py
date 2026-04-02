"""CLI command: run batch prediction from a CSV file.

The real work (read CSV, run model, write results) lives in runtime.batch_prediction.
This file only defines the command-line interface (typer).
"""

import os
from pathlib import Path

import typer

from runtime.batch_prediction.read_input_csv import read_property_rows
from runtime.batch_prediction.run_estimates import run_estimates_on_dataframe
from runtime.batch_prediction.write_output_csv import write_output_csv
from runtime.inference.load_artifact import load_artifact_from_path, ArtifactNotFoundError

batch_app = typer.Typer(help="Run batch prediction from CSV.")


@batch_app.command("run")
def run_batch(
    input_csv: Path = typer.Option(..., "--input", "-i", path_type=Path, help="Input CSV path"),
    output_csv: Path = typer.Option(..., "--output", "-o", path_type=Path, help="Output CSV path"),
    model_path: Path = typer.Option(None, "--model", "-m", path_type=Path, help="Model file (or set CESAR_MODEL_PATH)"),
    contract_path: Path = typer.Option(None, "--contract", "-c", path_type=Path, help="Contract file (or set CESAR_CONTRACT_PATH)"),
    separator: str = typer.Option(";", "--sep", "-s", help="CSV separator"),
) -> None:
    """Read CSV, run estimates, write results to output CSV."""
    model = model_path or Path(os.environ.get("CESAR_MODEL_PATH", ""))
    contract = contract_path or Path(os.environ.get("CESAR_CONTRACT_PATH", ""))

    if not model or not model.exists():
        typer.echo("Error: model path not set or file not found. Use --model or CESAR_MODEL_PATH.", err=True)
        raise typer.Exit(1)
    if not contract or not contract.exists():
        typer.echo("Error: contract path not set or file not found. Use --contract or CESAR_CONTRACT_PATH.", err=True)
        raise typer.Exit(1)

    try:
        model_obj, contract_obj = load_artifact_from_path(model, contract)
    except ArtifactNotFoundError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

    df = read_property_rows(input_csv, separator=separator)
    estimates = run_estimates_on_dataframe(df, model_obj, contract_obj)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    write_output_csv(df, estimates, output_csv, separator=separator)
    typer.echo(f"Wrote {len(estimates)} estimates to {output_csv}.")
