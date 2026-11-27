from datetime import datetime

import pandas as pd

from src.data.fyers_client import fyers

data = {
    "symbol": "NSE:RELIANCE-EQ",
    "resolution": "D",
    "date_format": "1",
    "range_from": "2025-07-28",
    "range_to": "2026-07-28",
    "cont_flag": "1"
}

response = fyers.history(data)

candles = response["candles"]

df = pd.DataFrame(
    candles,
    columns=[
        "timestamp",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ],
)

df["date"] = pd.to_datetime(df["timestamp"], unit="s")
df["symbol"] = "NSE:RELIANCE-EQ"

df = df[
    [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]
]

print(df.head())