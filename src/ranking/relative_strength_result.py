from dataclasses import dataclass


@dataclass(slots=True)
class RelativeStrengthResult:
    symbol: str
    score: float
    rs_rank: int