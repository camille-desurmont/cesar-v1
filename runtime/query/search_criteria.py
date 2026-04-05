from pydantic import BaseModel, Field


class SearchCriteria(BaseModel):
    """Structured search filters extracted from a natural language query."""

    type_local: str | None = Field(None, description="Property type: Appartement, Maison, Dépendance, or Local industriel. commercial ou assimilé")
    min_surface: float | None = Field(None, description="Minimum living area in m²")
    max_surface: float | None = Field(None, description="Maximum living area in m²")
    min_rooms: int | None = Field(None, description="Minimum number of main rooms")
    max_rooms: int | None = Field(None, description="Maximum number of main rooms")
    min_price: float | None = Field(None, description="Minimum transaction price in EUR")
    max_price: float | None = Field(None, description="Maximum transaction price in EUR")
    code_postal: list[str] | None = Field(None, description="List of postal codes (e.g. [\"75011\", \"75017\"])")
    nom_commune: str | None = Field(None, description="Commune name (partial match)")
    adresse_nom_voie: str | None = Field(None, description="Street name (partial match)")