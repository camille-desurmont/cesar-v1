from pathlib import Path

import pandas as pd

from runtime.query.search_criteria import SearchCriteria


def load_apartment_data(csv_path: Path) -> pd.DataFrame:
    """Load the DVF CSV data."""
    return pd.read_csv(csv_path, sep=";", dtype=str)


def search_properties(df: pd.DataFrame, criteria: SearchCriteria) -> pd.DataFrame:
    """Filter the DataFrame based on search criteria. Each non-None field adds a filter."""
    # Convert numeric columns from string
    df = df.copy()
    df["surface_reelle_bati"] = pd.to_numeric(df["surface_reelle_bati"], errors="coerce")
    df["nombre_pieces_principales"] = pd.to_numeric(df["nombre_pieces_principales"], errors="coerce")
    df["valeur_fonciere"] = pd.to_numeric(df["valeur_fonciere"], errors="coerce")

    # Keep only open-market sales above a realistic minimum price.
    # DVF includes exchanges, court sales, off-plan and other transaction types
    # that don't reflect market value and would distort results.
    mask = (df["nature_mutation"] == "Vente") & (df["valeur_fonciere"] > 10_000)

    if criteria.type_local is not None:
        mask &= df["type_local"].str.lower() == criteria.type_local.lower()

    if criteria.min_surface is not None:
        mask &= df["surface_reelle_bati"] >= criteria.min_surface

    if criteria.max_surface is not None:
        mask &= df["surface_reelle_bati"] <= criteria.max_surface

    if criteria.min_rooms is not None:
        mask &= df["nombre_pieces_principales"] >= criteria.min_rooms

    if criteria.max_rooms is not None:
        mask &= df["nombre_pieces_principales"] <= criteria.max_rooms

    if criteria.min_price is not None:
        mask &= df["valeur_fonciere"] >= criteria.min_price

    if criteria.max_price is not None:
        mask &= df["valeur_fonciere"] <= criteria.max_price

    if criteria.code_postal is not None:
        mask &= df["code_postal"].isin(criteria.code_postal)

    if criteria.nom_commune is not None:
        mask &= df["nom_commune"].str.contains(criteria.nom_commune, case=False, na=False)

    if criteria.adresse_nom_voie is not None:
        mask &= df["adresse_nom_voie"].str.contains(criteria.adresse_nom_voie, case=False, na=False)

    return df[mask]