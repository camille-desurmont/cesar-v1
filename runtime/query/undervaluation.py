"""Undervaluation detection for property search results.

For each match with both an actual transaction price and an ML estimate,
we compute a discount percentage and flag properties that appear undervalued.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from runtime.query.query_pipeline import PropertyMatch


def flag_undervalued(
    matches: list[PropertyMatch],
    threshold_pct: float = 20.0,
) -> list[PropertyMatch]:
    """Annotate each match with undervaluation signals.

    For a match to be scored, both ``actual_price_eur`` and
    ``estimated_price_eur`` must be present and the estimate must be positive.

    Fields set on each scored match:
    - ``discount_pct``  – how much cheaper than the ML estimate (%)
                          positive means actual < estimate (potential deal)
    - ``is_undervalued`` – True when discount_pct >= threshold_pct
    - ``value_rank``    – rank among all scored matches (1 = best deal)

    Matches that cannot be scored keep all three fields as None.

    Args:
        matches: Result list from the query pipeline.
        threshold_pct: Minimum discount (%) to flag a property as undervalued.

    Returns:
        Same list with undervaluation fields populated in-place.
    """
    scoreable_indices: list[int] = []
    discounts: list[float] = []

    for i, match in enumerate(matches):
        actual = match.actual_price_eur
        estimated = match.estimated_price_eur
        if actual is not None and estimated is not None and estimated > 0:
            discount = (estimated - actual) / estimated * 100
            scoreable_indices.append(i)
            discounts.append(discount)

    if not scoreable_indices:
        return matches

    # Rank: index 0 in sorted order → best deal (highest discount)
    ranked_order = sorted(range(len(discounts)), key=lambda k: discounts[k], reverse=True)
    # value_rank[k] = rank of the k-th scoreable match (1-based)
    value_ranks: list[int] = [0] * len(discounts)
    for rank, k in enumerate(ranked_order, start=1):
        value_ranks[k] = rank

    for k, i in enumerate(scoreable_indices):
        match = matches[i]
        discount = round(discounts[k], 1)
        matches[i] = match.model_copy(update={
            "discount_pct": discount,
            "is_undervalued": discount >= threshold_pct,
            "value_rank": value_ranks[k],
        })

    return matches
