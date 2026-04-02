from pathlib import Path

import pandas as pd


# We append the estimate column to the input dataframe so the output keeps all original columns plus
# the new one. That way downstream steps (e.g. reporting) have both inputs and outputs. Using a
# configurable output_column name makes it easy to change without touching callers.
def write_output_csv(
    df: pd.DataFrame,
    estimated_values: pd.Series | list[float],
    output_path: Path,
    output_column: str = "estimated_value_eur",
    separator: str = ";",
) -> None:
    out = df.copy()
    out[output_column] = estimated_values
    out.to_csv(output_path, sep=separator, index=False)
