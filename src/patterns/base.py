from dataclasses import dataclass

import pandas as pd

from src.config.settings import (
    BASE_MAX_DEPTH_PCT,
    BASE_MIN_DURATION_WEEKS,
    BASE_MIN_PRIOR_UPTREND_PCT,
    BASE_SWING_LOOKBACK,
)
from src.indicators.volume import volume_trend_slope
from src.patterns.swing import find_swings
from src.patterns.swing_filter import filter_swings


@dataclass(slots=True)
class BaseResult:
    detected: bool
    duration_weeks: int | None = None
    start_date: str | None = None
    high: float | None = None
    low: float | None = None
    volume_trend: str | None = None
    reason: str = ""
    # Integer bar index of the anchor swing high — added for
    # detect_vcp_contractions() to slice df to this same base window
    # without re-deriving the anchor itself. None whenever no anchor was
    # found at all (start_date/high/low are None too in that case).
    anchor_index: int | None = None


def detect_base(
    df: pd.DataFrame,
    min_prior_uptrend_pct: float = BASE_MIN_PRIOR_UPTREND_PCT,
    min_duration_weeks: int = BASE_MIN_DURATION_WEEKS,
    max_depth_pct: float = BASE_MAX_DEPTH_PCT,
    swing_lookback: int = BASE_SWING_LOOKBACK,
) -> BaseResult:
    """
    Approximates Minervini-style base/consolidation detection from price
    data alone: anchor on the most recent swing high that was preceded by
    a qualifying uptrend, then require price to still be contained under
    that high (no breakout) and within a bounded depth (not a downtrend)
    for at least min_duration_weeks.
    """
    swings = filter_swings(find_swings(df, lookback=swing_lookback))

    candidates = [
        curr
        for prev, curr in zip(swings, swings[1:])
        if prev.kind == "LOW"
        and curr.kind == "HIGH"
        and (curr.price - prev.price) / prev.price * 100 >= min_prior_uptrend_pct
    ]

    if not candidates:
        return BaseResult(
            detected=False,
            reason="no qualifying prior uptrend into a swing high",
        )

    anchor = candidates[-1]
    post = df.iloc[anchor.index:]

    if len(post) < 2:
        return BaseResult(
            detected=False,
            reason="not enough bars since the swing high",
        )

    if (post["close"] > anchor.price).any():
        return BaseResult(
            detected=False,
            reason="price has already broken out above the base high",
            anchor_index=anchor.index,
        )

    base_low = float(post["low"].min())
    depth_pct = (anchor.price - base_low) / anchor.price * 100

    if depth_pct > max_depth_pct:
        return BaseResult(
            detected=False,
            reason=f"depth {depth_pct:.1f}% exceeds max base depth {max_depth_pct:.1f}%",
            anchor_index=anchor.index,
        )

    start_date = df.iloc[anchor.index]["date"]
    end_date = df.iloc[-1]["date"]
    duration_weeks = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days // 7

    detected = duration_weeks >= min_duration_weeks

    # Volume dry-up check, scoped to the base window (anchor -> most recent
    # bar) rather than a fixed trailing lookback — reuses volume_trend_slope()
    # as-is, just with n set to the base's own bar count.
    volume_trend = volume_trend_slope(df, n=len(post))["classification"]

    return BaseResult(
        detected=detected,
        duration_weeks=duration_weeks,
        start_date=start_date,
        high=anchor.price,
        low=base_low,
        volume_trend=volume_trend,
        reason=(
            ""
            if detected
            else f"duration {duration_weeks}w below minimum {min_duration_weeks}w"
        ),
        anchor_index=anchor.index,
    )
