import pandas as pd


def rolling_high(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).max()


def rolling_low(series: pd.Series, period: int) -> pd.Series:
    return series.rolling(window=period).min()


def add_high_low(df: pd.DataFrame) -> pd.DataFrame:
    df["HIGH_52W"] = rolling_high(df["high"], 252)
    df["LOW_52W"] = rolling_low(df["low"], 252)

    return df