from datetime import datetime, timedelta
import time

import pandas as pd

from src.data.fyers_client import fyers


def download_history(symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    frames = []

    while start <= end:
        chunk_end = min(start + timedelta(days=365), end)

        data = {
            "symbol": symbol,
            "resolution": "D",
            "date_format": "1",
            "range_from": start.strftime("%Y-%m-%d"),
            "range_to": chunk_end.strftime("%Y-%m-%d"),
            "cont_flag": "1",
        }

        MAX_RETRIES = 3

        for attempt in range(MAX_RETRIES):
            response = fyers.history(data)

            # Success
            if response.get("s") == "ok":
                break

            # TEMPORARY DEBUG — raw response body for every non-"ok" result.
            # Added to confirm/rule out a suspected root cause: a live run
            # hit ~350 "code -16" auth failures (visible in terminal) that
            # never showed up as status="error" in update_all_symbols()'s
            # results — meaning something below is silently absorbing them,
            # most likely the no_data branch. Remove once confirmed and
            # the classification below is fixed accordingly.
            print(f"DEBUG RAW RESPONSE — {symbol} "
                  f"({start:%Y-%m-%d} to {chunk_end:%Y-%m-%d}): {response}")

            # No data for this date range (IPO not yet listed)
            if response.get("s") == "no_data":
                print(
                    f"No data for {symbol} "
                    f"({start.strftime('%Y-%m-%d')} to {chunk_end.strftime('%Y-%m-%d')})"
                )
                response = None
                break

            # Retry on rate limit
            if response.get("code") == 429:
                wait = 5 * (attempt + 1)
                print(f"Rate limit hit. Retrying in {wait} seconds...")
                time.sleep(wait)
                continue

            raise Exception(response)
        else:
            raise Exception("Maximum retries exceeded.")

        # Skip chunks with no data
        if response is None:
            start = chunk_end + timedelta(days=1)
            continue

        df = pd.DataFrame(
            response["candles"],
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ],
        )

        df["date"] = pd.to_datetime(df["timestamp"], unit="s").dt.strftime("%Y-%m-%d")
        df["symbol"] = symbol

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

        frames.append(df)

        start = chunk_end + timedelta(days=1)

    # Entire requested period has no data
    if not frames:
        return pd.DataFrame(
            columns=[
                "symbol",
                "date",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ]
        )

    return (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset=["symbol", "date"])
        .sort_values("date")
        .reset_index(drop=True)
    )