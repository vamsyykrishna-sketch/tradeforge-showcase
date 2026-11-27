import pandas as pd

from src.config.settings import (
    DISTRIBUTION_DAY_DECLINE_PCT,
    DISTRIBUTION_DAY_WINDOW,
    FOLLOW_THROUGH_LOOKBACK,
    FOLLOW_THROUGH_MIN_DAY,
    FOLLOW_THROUGH_MIN_GAIN_PCT,
)
from src.indicators.moving_average import add_moving_averages


def sma_status(df: pd.DataFrame) -> dict:
    df = add_moving_averages(df)
    latest = df.iloc[-1]

    return {
        "close": latest["close"],
        "sma_50": latest["SMA_50"],
        "sma_200": latest["SMA_200"],
        "above_sma_50": bool(latest["close"] > latest["SMA_50"]) if pd.notna(latest["SMA_50"]) else None,
        "above_sma_200": bool(latest["close"] > latest["SMA_200"]) if pd.notna(latest["SMA_200"]) else None,
        "sma_200_rising": bool(latest["SMA_200_RISING"]) if pd.notna(latest["SMA_200_RISING"]) else None,
    }


def distribution_day_count(
    df: pd.DataFrame,
    window: int = DISTRIBUTION_DAY_WINDOW,
    decline_threshold_pct: float = DISTRIBUTION_DAY_DECLINE_PCT,
) -> int:
    df = df.copy()
    df["prior_close"] = df["close"].shift(1)
    df["prior_volume"] = df["volume"].shift(1)
    df["pct_change"] = (df["close"] - df["prior_close"]) / df["prior_close"] * 100

    is_distribution = (df["pct_change"] <= -decline_threshold_pct) & (
        df["volume"] > df["prior_volume"]
    )

    return int(is_distribution.tail(window).sum())


def follow_through_day(
    df: pd.DataFrame,
    lookback: int = FOLLOW_THROUGH_LOOKBACK,
    min_day: int = FOLLOW_THROUGH_MIN_DAY,
    min_gain_pct: float = FOLLOW_THROUGH_MIN_GAIN_PCT,
) -> dict:
    """Simplified follow-through day detection: finds the swing low in the
    trailing `lookback` window, treats the first up-close day after it as
    rally day 1, then looks for the first day on/after `min_day` with a
    close gain >= min_gain_pct on volume higher than the prior day.
    """
    window = df.tail(lookback).reset_index(drop=True)

    if len(window) < 2:
        return {"detected": False, "reason": "insufficient_data"}

    window["prior_close"] = window["close"].shift(1)
    window["prior_volume"] = window["volume"].shift(1)
    window["pct_change"] = (
        (window["close"] - window["prior_close"]) / window["prior_close"] * 100
    )

    low_idx = window["close"].idxmin()

    up_days = window.index[(window.index > low_idx) & (window["pct_change"] > 0)]

    if len(up_days) == 0:
        return {
            "detected": False,
            "reason": "no rally attempt found off the swing low",
            "swing_low_date": window.loc[low_idx, "date"],
        }

    day1_idx = up_days[0]

    for idx in window.index[window.index >= day1_idx]:
        rally_day = idx - day1_idx + 1

        if rally_day < min_day:
            continue

        row = window.loc[idx]

        if row["pct_change"] >= min_gain_pct and row["volume"] > row["prior_volume"]:
            return {
                "detected": True,
                "date": row["date"],
                "rally_day": int(rally_day),
                "gain_pct": round(row["pct_change"], 2),
                "day1_date": window.loc[day1_idx, "date"],
            }

    return {
        "detected": False,
        "reason": "no follow-through day found after rally day 1",
        "day1_date": window.loc[day1_idx, "date"],
    }
