import pandas as pd

from src.config.settings import (
    TREND_TEMPLATE_ABOVE_52W_LOW_FACTOR,
    TREND_TEMPLATE_NEAR_52W_HIGH_FACTOR,
)
from src.scanner.rule_result import RuleResult


def rule_1(df: pd.DataFrame) -> RuleResult:
    """Price above 150 & 200 SMA"""

    latest = df.iloc[-1]

    if pd.isna(latest["SMA_150"]) or pd.isna(latest["SMA_200"]):
        return RuleResult(
            name="Price above 150 & 200 SMA",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    passed = (
        latest["close"] > latest["SMA_150"]
        and latest["close"] > latest["SMA_200"]
    )

    return RuleResult(
        name="Price above 150 & 200 SMA",
        passed=passed,
        actual={
            "close": float(latest["close"]),
            "sma_150": float(latest["SMA_150"]),
            "sma_200": float(latest["SMA_200"]),
        },
    )


def rule_2(df: pd.DataFrame) -> RuleResult:
    """150 SMA above 200 SMA"""

    latest = df.iloc[-1]

    if pd.isna(latest["SMA_150"]) or pd.isna(latest["SMA_200"]):
        return RuleResult(
            name="150 SMA above 200 SMA",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    passed = latest["SMA_150"] > latest["SMA_200"]

    return RuleResult(
        name="150 SMA above 200 SMA",
        passed=passed,
        actual={
            "sma_150": float(latest["SMA_150"]),
            "sma_200": float(latest["SMA_200"]),
        },
    )


def rule_3(df: pd.DataFrame) -> RuleResult:
    """200 SMA rising"""

    latest = df.iloc[-1]

    if pd.isna(latest["SMA_200"]) or pd.isna(latest["SMA_200_RISING"]):
        return RuleResult(
            name="200 SMA rising",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    passed = bool(latest["SMA_200_RISING"])

    return RuleResult(
        name="200 SMA rising",
        passed=passed,
        actual={
            "sma_200": float(latest["SMA_200"]),
            "rising": bool(latest["SMA_200_RISING"]),
        },
    )


def rule_4(df: pd.DataFrame) -> RuleResult:
    """50 SMA above 150 & 200 SMA"""

    latest = df.iloc[-1]

    if (
        pd.isna(latest["SMA_50"])
        or pd.isna(latest["SMA_150"])
        or pd.isna(latest["SMA_200"])
    ):
        return RuleResult(
            name="50 SMA above 150 & 200 SMA",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    passed = (
        latest["SMA_50"] > latest["SMA_150"]
        and latest["SMA_50"] > latest["SMA_200"]
    )

    return RuleResult(
        name="50 SMA above 150 & 200 SMA",
        passed=passed,
        actual={
            "sma_50": float(latest["SMA_50"]),
            "sma_150": float(latest["SMA_150"]),
            "sma_200": float(latest["SMA_200"]),
        },
    )


def rule_5(df: pd.DataFrame) -> RuleResult:
    """Price above 50 SMA"""

    latest = df.iloc[-1]

    if pd.isna(latest["SMA_50"]):
        return RuleResult(
            name="Price above 50 SMA",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    passed = latest["close"] > latest["SMA_50"]

    return RuleResult(
        name="Price above 50 SMA",
        passed=passed,
        actual={
            "close": float(latest["close"]),
            "sma_50": float(latest["SMA_50"]),
        },
    )


def rule_6(df: pd.DataFrame) -> RuleResult:
    """Price within 25% of 52-week high"""

    latest = df.iloc[-1]

    if pd.isna(latest["HIGH_52W"]):
        return RuleResult(
            name="Price within 25% of 52-week high",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    threshold = latest["HIGH_52W"] * TREND_TEMPLATE_NEAR_52W_HIGH_FACTOR
    passed = latest["close"] >= threshold

    return RuleResult(
        name="Price within 25% of 52-week high",
        passed=passed,
        actual={
            "close": float(latest["close"]),
            "high_52w": float(latest["HIGH_52W"]),
            "threshold": float(threshold),
        },
    )


def rule_7(df: pd.DataFrame) -> RuleResult:
    """Price at least 30% above 52-week low"""

    latest = df.iloc[-1]

    if pd.isna(latest["LOW_52W"]):
        return RuleResult(
            name="Price at least 30% above 52-week low",
            passed=False,
            actual={"reason": "Insufficient history"},
        )

    threshold = latest["LOW_52W"] * TREND_TEMPLATE_ABOVE_52W_LOW_FACTOR
    passed = latest["close"] >= threshold

    return RuleResult(
        name="Price at least 30% above 52-week low",
        passed=passed,
        actual={
            "close": float(latest["close"]),
            "low_52w": float(latest["LOW_52W"]),
            "threshold": float(threshold),
        },
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


def evaluate(df: pd.DataFrame) -> list[RuleResult]:
    """Evaluate all Trend Template rules."""
    return [rule(df) for rule in RULES]