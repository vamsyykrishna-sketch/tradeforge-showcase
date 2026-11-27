import pandas as pd

from src.config.settings import (
    BASE_SWING_LOOKBACK,
    VCP_MIN_CONTRACTIONS,
    VCP_TIGHTENING_TOLERANCE_PCT,
)
from src.patterns.base import BaseResult
from src.patterns.contraction import detect_contractions, find_vcp_contractions
from src.patterns.swing import find_swings
from src.patterns.swing_filter import filter_swings
from src.patterns.vcp_result import VCPResult


def detect_vcp_contractions(
    df: pd.DataFrame,
    base: BaseResult,
    min_contractions: int = VCP_MIN_CONTRACTIONS,
    tolerance: float = VCP_TIGHTENING_TOLERANCE_PCT,
    swing_lookback: int = BASE_SWING_LOOKBACK,
) -> VCPResult:
    """Display-only — never gates trend_template_passed/rs_passed/passed
    in scanner.py, same as BaseResult. Requires an already-detected base
    (BaseResult.detected) to have a window to sequence within at all."""
    if not base.detected or base.anchor_index is None:
        return VCPResult(
            detected=False,
            contractions=[],
            reason="no detected base to sequence contractions within",
        )

    contractions = detect_contractions(
        df, start_index=base.anchor_index, swing_lookback=swing_lookback
    )
    sequence = find_vcp_contractions(contractions, tolerance=tolerance)

    # Re-derives the same swings detect_contractions() computed internally,
    # just to check whether the window ends on an unpaired HIGH (price
    # still pulling back, no confirmed LOW yet per find_swings()'s
    # lookback constraint) — kept separate from detect_contractions()
    # rather than having it return that flag too, so that function's
    # return type stays a plain list[Contraction] for its other callers.
    # Must run find_swings() on the same full, un-sliced df — see
    # detect_contractions()'s docstring for why slicing df first would
    # silently renumber every swing index.
    swings = [
        s for s in filter_swings(find_swings(df, lookback=swing_lookback))
        if s.index >= base.anchor_index
    ]
    trailing_unconfirmed = bool(swings) and swings[-1].kind == "HIGH"
    unconfirmed_note = (
        " (most recent pullback still in progress — not yet a confirmed "
        "swing low, so not counted)"
        if trailing_unconfirmed
        else ""
    )

    if len(sequence) < min_contractions:
        return VCPResult(
            detected=False,
            contractions=sequence,
            reason=(
                f"only {len(sequence)} tightening contraction(s), "
                f"need {min_contractions}{unconfirmed_note}"
            ),
        )

    final = sequence[-1]
    pivot_price = final.high
    pivot_date = df.iloc[final.start_index]["date"]
    current_close = df.iloc[-1]["close"]
    pivot_distance_pct = (current_close - pivot_price) / pivot_price * 100

    return VCPResult(
        detected=True,
        contractions=sequence,
        reason=f"{len(sequence)} progressively tightening contractions found{unconfirmed_note}",
        pivot_price=pivot_price,
        pivot_date=pivot_date,
        pivot_distance_pct=pivot_distance_pct,
    )


def format_pivot_status(vcp: VCPResult) -> str:
    """Human-readable one-liner for the pivot + distance, for display
    layers (app.py, scanner/report.py) to call directly rather than each
    re-deriving wording from the raw pivot_distance_pct sign themselves."""
    if not vcp.detected or vcp.pivot_price is None:
        return "No confirmed pivot yet"

    if vcp.pivot_distance_pct >= 0:
        return (
            f"Pivot ₹{vcp.pivot_price:.2f} ({vcp.pivot_date}) — "
            f"already {vcp.pivot_distance_pct:.1f}% ABOVE pivot"
        )

    return (
        f"Pivot ₹{vcp.pivot_price:.2f} ({vcp.pivot_date}) — "
        f"{abs(vcp.pivot_distance_pct):.1f}% BELOW pivot"
    )