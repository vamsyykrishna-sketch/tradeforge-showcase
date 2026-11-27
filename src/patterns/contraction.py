from dataclasses import dataclass

import pandas as pd

from src.config.settings import BASE_SWING_LOOKBACK, VCP_TIGHTENING_TOLERANCE_PCT
from src.patterns.swing import find_swings
from src.patterns.swing_filter import filter_swings


@dataclass(slots=True)
class Contraction:
    start_index: int  # index of the HIGH swing starting this pullback leg
    end_index: int    # index of the LOW swing ending it

    high: float
    low: float

    contraction_pct: float


def detect_contractions(
    df: pd.DataFrame,
    start_index: int = 0,
    swing_lookback: int = BASE_SWING_LOOKBACK,
) -> list[Contraction]:
    """Pairs consecutive (HIGH, LOW) swings into contractions — each pair
    is one pullback leg, depth% = (high-low)/high*100.

    df must be the FULL, un-sliced price DataFrame — NOT pre-sliced to
    the base window. find_swings()/.iloc index positions are relative to
    whatever DataFrame is passed to them, so slicing df before calling
    this (e.g. df.iloc[base.anchor_index:]) would silently renumber every
    swing to be relative to the slice's own start instead of df's —
    exactly the bug this signature exists to avoid, since callers need
    Contraction.start_index/end_index to line up with BaseResult.
    anchor_index's own positional space (and with df itself) for any
    downstream df.iloc[...] lookup (dates, prices) to be correct.
    start_index (typically BaseResult.anchor_index) instead restricts
    which swings are eligible to START a contraction, applied AFTER
    swing detection runs on the full df.

    A trailing, unpaired HIGH swing (price still pulling back, no
    confirmed LOW yet) is never returned as a contraction here — see
    find_swings()'s lookback constraint. Callers that need to know
    whether that's the case (detect_vcp_contractions() does, for its
    VCPResult.reason) check for it separately.
    """
    swings = filter_swings(find_swings(df, lookback=swing_lookback))
    swings = [s for s in swings if s.index >= start_index]

    contractions = []
    for prev, curr in zip(swings, swings[1:]):
        if prev.kind == "HIGH" and curr.kind == "LOW":
            pct = (prev.price - curr.price) / prev.price * 100
            contractions.append(
                Contraction(
                    start_index=prev.index,
                    end_index=curr.index,
                    high=prev.price,
                    low=curr.price,
                    contraction_pct=pct,
                )
            )

    return contractions


def find_vcp_contractions(
    contractions: list[Contraction],
    tolerance: float = VCP_TIGHTENING_TOLERANCE_PCT,
) -> list[Contraction]:
    """Longest CONSECUTIVE run of tightening contractions starting from
    the earliest one in the base window. Stops at the first contraction
    that widens beyond the previous accepted one plus tolerance, rather
    than skipping it and continuing to compare later ones against the
    last accepted contraction — a VCP requires the sequence itself to
    tighten leg over leg, so a widened leg in the middle breaks the
    sequence rather than just being an outlier to ignore."""
    if not contractions:
        return []

    sequence = [contractions[0]]

    for current in contractions[1:]:
        previous = sequence[-1]

        if current.contraction_pct <= previous.contraction_pct + tolerance:
            sequence.append(current)
        else:
            break

    return sequence