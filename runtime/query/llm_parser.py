import os

import anthropic

from runtime.query.search_criteria import SearchCriteria


SYSTEM_PROMPT = """You are a search filter extractor for a French real estate transaction database.
The database contains properties across all Paris districts (code postal 75001 - 75020).

Available columns and their meanings:
- surface_reelle_bati: living area in m²
- nombre_pieces_principales: number of main rooms
- valeur_fonciere: transaction price in EUR
- type_local: one of Appartement, Maison, Dépendance, Local industriel. commercial ou assimilé
- code_postal: list of postal codes to search (e.g. ["75011", "75017"] for 11th and 17th)
- nom_commune: commune name (e.g. Paris 15e Arrondissement)
- adresse_nom_voie: street name (e.g. RUE ANDRE GIDE)

Rules:
- Convert prices in "k" to thousands (500k = 500000)
- If user says "3 rooms" or "3 pièces", set both min_rooms and max_rooms to 3
- "under X" or "moins de X" → set max_price. "over X" or "plus de X" → set min_price
- Only set fields that are explicitly mentioned or clearly implied
- Handle both French and English queries
"""


def parse_query(user_query: str) -> SearchCriteria:
    """Parse a natural language query into structured search criteria using Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("Set ANTHROPIC_API_KEY environment variable to use the query command.")

    client = anthropic.Anthropic(api_key=api_key)

    # Define the tool with SearchCriteria's JSON schema as input
    tool_schema = SearchCriteria.model_json_schema()
    tools = [
        {
            "name": "extract_search_criteria",
            "description": "Extract structured search filters from the user's natural language query.",
            "input_schema": tool_schema,
        }
    ]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=tools,
        tool_choice={"type": "tool", "name": "extract_search_criteria"},
        messages=[{"role": "user", "content": user_query}],
    )

    # Extract the tool call arguments
    for block in response.content:
        if block.type == "tool_use":
            return SearchCriteria.model_validate(block.input)

    raise RuntimeError("LLM did not return a tool call. This should not happen with forced tool_choice.")