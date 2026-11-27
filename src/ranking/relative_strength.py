from src.data.price_repository import load_candles
from src.data.symbol_repository import get_active_symbols
from src.ranking.momentum import calculate_momentum
from src.ranking.relative_strength_result import RelativeStrengthResult


def calculate_relative_strength() -> list[RelativeStrengthResult]:
    scores = []

    for symbol in get_active_symbols():
        df = load_candles(symbol)

        if len(df) < 252:
            continue

        score = calculate_momentum(df)

        scores.append(
            RelativeStrengthResult(
                symbol=symbol,
                score=score,
                rs_rank=0,
            )
        )

    scores.sort(key=lambda x: x.score, reverse=True)

    total = len(scores)

    for index, stock in enumerate(scores):
        stock.rs_rank = round((total - index) / total * 100)

    return scores

def build_rs_map() -> dict[str, RelativeStrengthResult]:
    rs_list = calculate_relative_strength()

    return {
        stock.symbol: stock
        for stock in rs_list
    }