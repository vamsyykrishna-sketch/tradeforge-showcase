import pandas as pd
from src.indicators.trend import is_rising
from src.indicators.high_low import rolling_high, rolling_low

def sma(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).mean()


def add_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["SMA_50"] = sma(df["close"], 50)
    df["SMA_150"] = sma(df["close"], 150)
    df["SMA_200"] = sma(df["close"], 200)
    df["SMA_200_RISING"] = is_rising(df["SMA_200"], periods=20)
    df["HIGH_52W"] = rolling_high(df["high"], 252)
    df["LOW_52W"] = rolling_low(df["low"], 252)

    return df