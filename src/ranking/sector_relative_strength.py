import statistics

from src.data.symbol_industry_repository import get_all_symbol_industries
from src.ranking.relative_strength_result import RelativeStrengthResult


def calculate_sector_relative_strength(
    rs_map: dict[str, RelativeStrengthResult],
) -> dict[str, float]:
    """Sector RS = median of member stocks' already-computed rs_rank,
    grouped by industry (src.data.symbol_industry_repository, NSE's own
    classification -- see conversation on why no new momentum calc is
    needed here). Median, not mean -- resistant to one outlier stock
    dragging a thin sector's number, per conversation.

    Symbols with no symbol_industry row (populate_index() not yet re-run
    for their index, or a symbol outside all 5 index CSVs) are simply
    excluded from any group -- no crash, no default bucket."""
    symbol_industries = get_all_symbol_industries()

    ranks_by_industry: dict[str, list[int]] = {}
    for symbol, result in rs_map.items():
        industry = symbol_industries.get(symbol)
        if industry is None:
            continue
        ranks_by_industry.setdefault(industry, []).append(result.rs_rank)

    return {
        industry: round(statistics.median(ranks))
        for industry, ranks in ranks_by_industry.items()
    }
