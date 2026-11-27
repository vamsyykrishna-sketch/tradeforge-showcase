from src.data.symbol_repository import add_symbol, symbol_exists
from src.data.symbol_universe_repository import add_symbol_universe
from src.data.symbol_industry_repository import add_symbol_industry
from src.universe.loader import load_index


def populate_index(index_name: str) -> tuple[int, int]:
    symbol_industry_pairs = load_index(index_name)

    added = 0
    skipped = 0

    for symbol, industry in symbol_industry_pairs:
        ticker = symbol.split(":", 1)[-1]

        if ticker.upper().startswith("DUMMY"):
            skipped += 1
            continue

        if symbol_exists(symbol):
            skipped += 1
        else:
            add_symbol(symbol)
            added += 1

        add_symbol_universe(symbol, index_name)
        add_symbol_industry(symbol, industry)

    return added, skipped