from src.config.settings import RS_RANK_CUTOFF
from src.scanner.rule_result import RuleResult


def print_stock_report(result: dict) -> None:
    print(f"\n{result['symbol']}")

    for rule in result["rules"]:
        rule: RuleResult

        status = "PASS" if rule.passed else "FAIL"
        print(f"\n{status} - {rule.name}")

        for key, value in rule.actual.items():
            if isinstance(value, float):
                value = round(value, 2)

            print(f"    {key}: {value}")

    rs = result["rs"]
    rs_rank = rs.rs_rank if rs else "N/A"

    print(f"\n{'PASS' if result['rs_passed'] else 'FAIL'} - RS Rank >= {RS_RANK_CUTOFF}")
    print(f"    rs_rank: {rs_rank}")

    base = result.get("base")
    if base is not None:
        duration = base.duration_weeks if base.duration_weeks is not None else "N/A"
        print(f"\nBase detected: {'Y' if base.detected else 'N'}, duration: {duration} weeks")
        if base.volume_trend is not None:
            print(f"    volume trend: {base.volume_trend}")
        if not base.detected and base.reason:
            print(f"    reason: {base.reason}")

    print(f"\nOverall: {'PASS' if result['passed'] else 'FAIL'}")

def print_summary(summary: dict) -> None:
    print("\n")
    print("=" * 60)
    print("TREND TEMPLATE SUMMARY")
    print("=" * 60)

    print(f"Total Stocks : {summary['total']}")
    print(f"Passed       : {summary['passed_count']}")
    print(f"Failed       : {summary['failed_count']}")