from src.config.settings import RS_RANK_CUTOFF
from src.data.price_repository import load_candles
from src.indicators.indicators import add_indicators
from src.patterns.base import detect_base
from src.patterns.vcp import detect_vcp_contractions
from src.scanner.evaluator import evaluate_trend_template


def scan_symbol(symbol: str, rs_map: dict) -> dict:
    try:
        df = load_candles(symbol)

        if df.empty:
            return {
                "symbol": symbol,
                "error": "No historical data",
            }

        df = add_indicators(df)

        results = evaluate_trend_template(df)

        rs = rs_map.get(symbol)
        trend_template_passed = results["passed"]
        rs_passed = rs is not None and rs.rs_rank >= RS_RANK_CUTOFF

        results["rs"] = rs
        results["trend_template_passed"] = trend_template_passed
        results["rs_passed"] = rs_passed
        results["passed"] = trend_template_passed and rs_passed

        # Display-only, per Minervini's base/consolidation framework — does
        # not participate in trend_template_passed/rs_passed/passed above.
        base = detect_base(df)
        results["base"] = base

        # Also display-only, same non-gating status as "base" above —
        # only meaningful once a base has actually been detected, since
        # it needs that window to sequence contractions within.
        results["vcp"] = detect_vcp_contractions(df, base)

        return {
            "symbol": symbol,
            **results,
        }

    except Exception as e:
        return {
            "symbol": symbol,
            "error": str(e),
        }


def scan_all_symbols(
    symbols: list[str],
    rs_map: dict,
) -> list[dict]:
    return [
        scan_symbol(symbol, rs_map)
        for symbol in symbols
    ]


def summarize_results(results: list[dict]) -> dict:
    passed = [r for r in results if r.get("passed", False)]
    failed = [r for r in results if not r.get("passed", False)]

    return {
        "total": len(results),
        "passed_count": len(passed),
        "failed_count": len(failed),
        "passed": passed,
        "failed": failed,
    }