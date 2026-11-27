import numpy as np
import pandas as pd

from src.config.settings import (
    VOLUME_TREND_SLOPE_LOOKBACK,
    VOLUME_TREND_SLOPE_THRESHOLD_PCT,
)


def add_volume_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["AVG_VOL_20"] = df["volume"].rolling(20).mean()
    df["AVG_VOL_50"] = df["volume"].rolling(50).mean()
    df["VOLUME_RATIO"] = df["volume"] / df["AVG_VOL_50"]

    return df


def volume_trend_slope(
    df: pd.DataFrame,
    n: int = VOLUME_TREND_SLOPE_LOOKBACK,
    threshold_pct: float = VOLUME_TREND_SLOPE_THRESHOLD_PCT,
) -> dict:
    window = df["volume"].tail(n)

    if len(window) < n:
        return {
            "slope": None,
            "slope_pct_per_day": None,
            "classification": "insufficient_data",
        }

    y = window.to_numpy()
    slope, _ = np.polyfit(range(n), y, 1)

    mean_volume = y.mean()
    slope_pct_per_day = (slope / mean_volume) if mean_volume else 0.0

    if slope_pct_per_day > threshold_pct:
        classification = "rising"
    elif slope_pct_per_day < -threshold_pct:
        classification = "declining"
    else:
        classification = "flat"

    return {
        "slope": slope,
        "slope_pct_per_day": slope_pct_per_day,
        "classification": classification,
    }