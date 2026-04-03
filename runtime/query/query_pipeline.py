from pathlib import Path
from typing import Any

from pydantic import BaseModel

from prediction_contract.request_schema import EstimateRequest
from prediction_contract.contract_version import ContractVersion
from runtime.inference.estimate_from_artifact import estimate_from_model
from runtime.inference.load_artifact import load_artifact_from_path
from runtime.query.llm_parser import parse_query
from runtime.query.search_criteria import SearchCriteria
from runtime.query.data_search import load_apartment_data, search_properties
from runtime.query.undervaluation import flag_undervalued


class PropertyMatch(BaseModel):
    adresse: str
    surface_m2: float | None
    rooms: int | None
    type_local: str
    actual_price_eur: float | None
    estimated_price_eur: float | None
    date_mutation: str
    code_postal: str
    discount_pct: float | None = None
    is_undervalued: bool | None = None
    value_rank: int | None = None


class QueryResult(BaseModel):
    query: str
    parsed_criteria: SearchCriteria
    total_matches: int
    matches: list[PropertyMatch]


def _enrich_with_estimate(
    row: dict, model: Any, contract: ContractVersion
) -> float | None:
    """Try to get an ML estimate for this row. Return None if not possible."""
    try:
        request = EstimateRequest(
            surface_reelle_bati=float(row.get("surface_reelle_bati", 0)),
            nombre_pieces_principales=float(row.get("nombre_pieces_principales", 0)),
            code_departement=str(row.get("code_departement", "75")),
            type_local=str(row.get("type_local", "Appartement")),
        )
        response = estimate_from_model(model, request, contract)
        return response.estimated_value_eur
    except Exception:
        return None


def run_query(
    user_query: str,
    csv_path: Path,
    model_path: Path | None = None,
    contract_path: Path | None = None,
    undervaluation_threshold_pct: float = 20.0,
) -> QueryResult:
    """Full pipeline: parse natural language → search data → enrich with ML estimates."""
    # 1. Parse the query
    criteria = parse_query(user_query)

    # 2. Load and filter data
    df = load_apartment_data(csv_path)
    results_df = search_properties(df, criteria)

    # 3. Optionally load the ML model
    model_obj = None
    contract_obj = None
    if model_path and contract_path and model_path.exists() and contract_path.exists():
        model_obj, contract_obj = load_artifact_from_path(model_path, contract_path)

    # 4. Build result list
    matches: list[PropertyMatch] = []
    for _, row in results_df.iterrows():
        estimated = None
        if model_obj and contract_obj:
            estimated = _enrich_with_estimate(row, model_obj, contract_obj)

        numero = str(row.get("adresse_numero", "")).replace("None", "").strip()
        voie = str(row.get("adresse_nom_voie", "")).strip()
        adresse = f"{numero} {voie}".strip()

        surface = row.get("surface_reelle_bati")
        rooms = row.get("nombre_pieces_principales")

        matches.append(PropertyMatch(
            adresse=adresse,
            surface_m2=float(surface) if surface and surface == surface else None,  # NaN check
            rooms=int(rooms) if rooms and rooms == rooms else None,
            type_local=str(row.get("type_local", "")),
            actual_price_eur=float(row["valeur_fonciere"]) if row.get("valeur_fonciere") and row["valeur_fonciere"] == row["valeur_fonciere"] else None,
            estimated_price_eur=estimated,
            date_mutation=str(row.get("date_mutation", "")),
            code_postal=str(row.get("code_postal", "")),
        ))

    flag_undervalued(matches, threshold_pct=undervaluation_threshold_pct)

    return QueryResult(
        query=user_query,
        parsed_criteria=criteria,
        total_matches=len(matches),
        matches=matches,
    )