import pandas as pd


def calculate_momentum(df: pd.DataFrame) -> float:
    """
    Calculate Minervini weighted momentum score.

    Weights:
    - 3 months : 40%
    - 6 months : 20%
    - 9 months : 20%
    - 12 months: 20%
    """

    if len(df) < 252:
        raise ValueError("Need at least 252 trading days.")

    close = df["close"]

    current = close.iloc[-1]

    r3 = current / close.iloc[-63] - 1
    r6 = current / close.iloc[-126] - 1
    r9 = current / close.iloc[-189] - 1
    r12 = current / close.iloc[-252] - 1

    return (
        0.40 * r3 +
        0.20 * r6 +
        0.20 * r9 +
        0.20 * r12
    )