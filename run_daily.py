from datetime import date, datetime
from pathlib import Path

from src.data.index_updater import update_all_indices
from src.data.price_repository import get_global_latest_date
from src.data.symbol_repository import get_active_symbols
from src.data.update_all import update_all_symbols
from src.market_context.report import print_market_context
from src.ranking.relative_strength import build_rs_map
from src.scanner.report import print_stock_report, print_summary
from src.scanner.scanner import scan_all_symbols, summarize_results

LOG_PATH = Path("logs/daily_run.log")


def _days_ago(date_str):
    d = datetime.strptime(date_str, "%Y-%m-%d").date()
    return (date.today() - d).days


def _classify(results):
    updated = [r for r in results if r["status"] == "updated"]
    no_data = [r for r in results if r["status"] == "no_data"]
    up_to_date = [r for r in results if r["status"] == "up_to_date"]
    errors = [r for r in results if r["status"] == "error"]

    has_errors = len(errors) > 0
    has_updates = len(updated) > 0
    has_other_success = len(no_data) > 0 or len(up_to_date) > 0

    if has_errors and not has_updates and not has_other_success:
        outcome = "failed"
    elif has_errors:
        outcome = "partial"
    elif has_updates:
        outcome = "advanced"
    else:
        outcome = "unchanged_holiday"

    return outcome, updated, no_data, up_to_date, errors


def _print_update_outcome(outcome, new_date, errors):
    if outcome in ("failed", "partial"):
        print("\n" + "=" * 60)
        print(
            f"⚠️  WARNING: Data update failed or incomplete — "
            f"{len(errors)} symbol(s) may be stale. "
            f"Results may not reflect current market conditions."
        )
        print("=" * 60)
        for r in errors:
            print(f"    FAILED: {r['symbol']} -> {r['detail']}")
        print("=" * 60 + "\n")
    elif outcome == "advanced":
        print(f"\nData updated successfully. Latest date: {new_date}\n")
    else:
        print(
            f"\nNo new data — Fyers confirms no data available for the missing "
            f"date(s) (consistent with a weekend/holiday). Data considered "
            f"current as of {new_date}.\n"
        )


def _log_run(prior_date, new_date, updated, no_data, errors, summary):
    LOG_PATH.parent.mkdir(exist_ok=True, parents=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_date_display = new_date if new_date != prior_date else "unchanged"
    error_symbols = ", ".join(r["symbol"] for r in errors)

    line = (
        f"{timestamp} | prior={prior_date} | new={new_date_display} | "
        f"updated={len(updated)} no_data={len(no_data)} errors={len(errors)}"
        + (f" ({error_symbols})" if error_symbols else "")
        + f" | scan_passed={summary['passed_count']}"
    )

    with LOG_PATH.open("a") as f:
        f.write(line + "\n")


def main():
    prior_date = get_global_latest_date()

    if prior_date is None:
        print("Data last updated: never (no data in database)")
    else:
        print(f"Data last updated: {prior_date} ({_days_ago(prior_date)} days ago)")

    print("Fetching missing data...\n")

    results = update_all_symbols()
    new_date = get_global_latest_date()

    outcome, updated, no_data, up_to_date, errors = _classify(results)
    _print_update_outcome(outcome, new_date, errors)

    index_results = update_all_indices()
    index_errors = [r for r in index_results if r["status"] == "error"]
    if index_errors:
        print(
            f"Note: {len(index_errors)} index update(s) failed "
            f"({', '.join(r['symbol'] for r in index_errors)}); "
            f"market context below may use slightly stale index data.\n"
        )

    symbols = get_active_symbols()
    rs_map = build_rs_map()
    scan_results = scan_all_symbols(symbols, rs_map)
    summary = summarize_results(scan_results)

    print_summary(summary)

    stale_symbols = {r["symbol"] for r in errors}

    for result in summary["passed"]:
        if result["symbol"] in stale_symbols:
            print(
                f"\n⚠️  STALE DATA — price update failed for "
                f"{result['symbol']} today; this result may not reflect "
                f"current market data."
            )
        print_stock_report(result)
        print_market_context(result["symbol"])

    _log_run(prior_date, new_date, updated, no_data, errors, summary)


if __name__ == "__main__":
    main()
