from src.data.symbol_repository import get_active_symbols
from src.ranking.relative_strength import build_rs_map
from src.scanner.scanner import scan_all_symbols, summarize_results
from src.scanner.report import print_summary, print_stock_report

symbols = get_active_symbols()

rs_map = build_rs_map()

results = scan_all_symbols(symbols, rs_map)

summary = summarize_results(results)

print_summary(summary)

for result in summary["passed"]:
    print_stock_report(result)