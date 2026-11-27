from dataclasses import dataclass


@dataclass
class SwingPoint:
    index: int
    price: float
    kind: str  # "HIGH" or "LOW"

import pandas as pd
def find_swings(df: pd.DataFrame, lookback: int = 5) -> list[SwingPoint]:
    """
    Detect swing highs and swing lows.

    A swing high is a high that is higher than the
    surrounding 'lookback' candles.

    A swing low is a low that is lower than the
    surrounding 'lookback' candles.
    """

    swings = []

    for i in range(lookback, len(df) - lookback):

        high = df.iloc[i]["high"]
        low = df.iloc[i]["low"]

        left_high = df.iloc[i - lookback:i]["high"].max()
        right_high = df.iloc[i + 1:i + lookback + 1]["high"].max()

        left_low = df.iloc[i - lookback:i]["low"].min()
        right_low = df.iloc[i + 1:i + lookback + 1]["low"].min()

        if high > left_high and high > right_high:
            swings.append(
                SwingPoint(
                    index=i,
                    price=float(high),
                    kind="HIGH",
                )
            )

        elif low < left_low and low < right_low:
            swings.append(
                SwingPoint(
                    index=i,
                    price=float(low),
                    kind="LOW",
                )
            )

    return swings