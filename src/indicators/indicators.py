from pandas import DataFrame

from src.indicators.moving_average import add_moving_averages
from src.indicators.high_low import add_high_low
from src.indicators.volume import add_volume_indicators


def add_indicators(df: DataFrame) -> DataFrame:
    df = add_moving_averages(df)
    df = add_high_low(df)
    df = add_volume_indicators(df)

    return df