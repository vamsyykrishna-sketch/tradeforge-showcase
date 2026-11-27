import pandas as pd


def is_rising(series: pd.Series, periods: int = 1) -> pd.Series:
    shifted = series.shift(periods)
    valid = series.notna() & shifted.notna()

    return (series > shifted).where(valid)