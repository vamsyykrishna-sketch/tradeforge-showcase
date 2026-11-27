from datetime import datetime, timedelta

from src.data.downloader import download_history
from src.data.price_repository import get_latest_date, save_candles


def update_history(symbol):
    latest = get_latest_date(symbol)

    if latest is None:
        print(f"First download for {symbol}")
        start = "2020-01-01"  # configurable later
    else:
        start = (
            datetime.strptime(latest, "%Y-%m-%d")
            + timedelta(days=1)
        ).strftime("%Y-%m-%d")

    end = datetime.today().strftime("%Y-%m-%d")

    if start > end:
        print(f"{symbol} is already up to date.")
        return {"symbol": symbol, "status": "up_to_date", "detail": None}

    df = download_history(symbol, start, end)

    if df.empty:
        print(f"No historical data available for {symbol}")
        return {"symbol": symbol, "status": "no_data", "detail": None}

    save_candles(df)

    print(f"Saved {len(df)} candles for {symbol}")

    return {
        "symbol": symbol,
        "status": "updated",
        "detail": f"{len(df)} candles, latest={df['date'].max()}",
    }