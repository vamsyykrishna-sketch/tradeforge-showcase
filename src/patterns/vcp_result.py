from dataclasses import dataclass

from src.patterns.contraction import Contraction


@dataclass(slots=True)
class VCPResult:
    # Display-only, never a pass/fail gate — named to match BaseResult's
    # own "detected" field rather than "passed".
    detected: bool

    contractions: list[Contraction]

    reason: str = ""

    # Pivot = the HIGH of the last (most recent, tightest) contraction in
    # the confirmed sequence — the level Minervini's framework treats as
    # the actionable breakout trigger. Only ever set when detected=True;
    # a partial/unconfirmed sequence has no earned pivot yet.
    pivot_price: float | None = None
    pivot_date: str | None = None
    # (current_close - pivot_price) / pivot_price * 100 — positive means
    # price is already above the pivot (breakout triggered), negative
    # means price is still that far below it. Raw number only, no
    # formatted text here — see vcp.py's format_pivot_status().
    pivot_distance_pct: float | None = None