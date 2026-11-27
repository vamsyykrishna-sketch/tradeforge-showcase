from src.data.index_price_repository import load_index_candles
from src.data.index_updater import INDEX_SYMBOLS
from src.data.symbol_universe_repository import get_universes_for_symbol
from src.market_context.indicators import (
    distribution_day_count,
    follow_through_day,
    sma_status,
)

REFERENCE_UNIVERSES = ["nifty50", "nifty500"]


def _index_context(fyers_symbol: str):
    df = load_index_candles(fyers_symbol)

    if df.empty:
        return None

    return {
        "sma": sma_status(df),
        "distribution_days": distribution_day_count(df),
        "follow_through": follow_through_day(df),
    }


def get_market_context_for_stock(symbol: str) -> dict:
    roles = {}

    for universe in get_universes_for_symbol(symbol):
        roles.setdefault(universe, "own universe")

    for universe in REFERENCE_UNIVERSES:
        roles.setdefault(universe, "reference")

    context = {}

    for universe, role in roles.items():
        fyers_symbol = INDEX_SYMBOLS.get(universe)

        if fyers_symbol is None:
            continue

        context[universe] = {
            "role": role,
            "index_symbol": fyers_symbol,
            "data": _index_context(fyers_symbol),
        }

    return context


def format_market_context(context: dict) -> str:
    order = sorted(
        context.keys(),
        key=lambda u: (context[u]["role"] != "own universe", u),
    )

    lines = []

    for universe in order:
        entry = context[universe]
        data = entry["data"]
        label = f"{universe} ({entry['role']})"

        if data is None:
            lines.append(f"  {label}: no index data available")
            continue

        sma = data["sma"]
        above_50 = (
            "above" if sma["above_sma_50"] is True
            else "below" if sma["above_sma_50"] is False
            else "n/a"
        )
        above_200 = (
            "above" if sma["above_sma_200"] is True
            else "below" if sma["above_sma_200"] is False
            else "n/a"
        )
        rising = (
            "rising" if sma["sma_200_rising"] is True
            else "flat/falling" if sma["sma_200_rising"] is False
            else "n/a"
        )

        ftd = data["follow_through"]
        ftd_text = (
            f"FTD confirmed {ftd['date']} (day {ftd['rally_day']}, +{ftd['gain_pct']}%)"
            if ftd["detected"]
            else "no confirmed follow-through day"
        )

        lines.append(
            f"  {label}: price {above_50} 50SMA, {above_200} 200SMA ({rising}); "
            f"{data['distribution_days']} distribution day(s) in last 25; {ftd_text}"
        )

    return "\n".join(lines)


def print_market_context(symbol: str) -> None:
    context = get_market_context_for_stock(symbol)

    if not context:
        print("  Market context: no universe/index data available")
        return

    print("  Market context:")
    print(format_market_context(context))
