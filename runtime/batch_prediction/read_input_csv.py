from pathlib import Path
from typing import Iterator

import pandas as pd

from prediction_contract.feature_schema import MODEL_FEATURE_NAMES, TARGET_NAME

# Validate required columns as soon as we read the file. Failing fast with a clear error (missing
# columns) is better than failing later inside the model with a cryptic index or key error. In
# production pipelines, early validation saves debugging time and makes logs actionable.
REQUIRED_INPUT_COLUMNS: list[str] = [
    "surface_reelle_bati",
    "nombre_pieces_principales",
    "code_departement",
    "type_local",
]


def read_property_rows(csv_path: Path, separator: str = ";") -> pd.DataFrame:
    df = pd.read_csv(csv_path, sep=separator, low_memory=False)
    missing = set(REQUIRED_INPUT_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Input CSV missing columns: {missing}")
    return df
