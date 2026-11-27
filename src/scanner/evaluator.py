from src.scanner.trend_template import (
    rule_1,
    rule_2,
    rule_3,
    rule_4,
    rule_5,
    rule_6,
    rule_7,
)

RULES = [
    rule_1,
    rule_2,
    rule_3,
    rule_4,
    rule_5,
    rule_6,
    rule_7,
]


def evaluate_trend_template(df) -> dict:
    rule_results = [rule(df) for rule in RULES]

    return {
        "passed": all(r.passed for r in rule_results),
        "rules": rule_results,
    }