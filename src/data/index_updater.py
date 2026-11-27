from datetime import datetime, timedelta

from src.data.downloader import download_history
from src.data.index_price_repository import get_latest_index_date, save_index_candles

# universe name -> Fyers index symbol, confirmed live against the History API.
# NIFTY500 is included as a reference index (not tied to any universe).
INDEX_SYMBOLS = {
    "nifty50": "NSE:NIFTY50-INDEX",
    "niftynext50": "NSE:NIFTYNXT50-INDEX",
    "niftymidcap150": "NSE:NIFTYMIDCAP150-INDEX",
    "niftysmallcap250": "NSE:NIFTYSMLCAP250-INDEX",
    "niftymicrocap250": "NSE:NIFTYMICROCAP250-INDEX",
    "nifty500": "NSE:NIFTY500-INDEX",
}


def update_index_history(index_symbol):
    latest = get_latest_index_date(index_symbol)

    if latest is None:
        print(f"First download for {index_symbol}")
        start = "2020-01-01"
    else:
        start = (
            datetime.strptime(latest, "%Y-%m-%d")
            + timedelta(days=1)
        ).strftime("%Y-%m-%d")

    end = datetime.today().strftime("%Y-%m-%d")

    if start > end:
        print(f"{index_symbol} is already up to date.")
        return {"symbol": index_symbol, "status": "up_to_date", "detail": None}

    df = download_history(index_symbol, start, end)

    if df.empty:
        print(f"No historical data available for {index_symbol}")
        return {"symbol": index_symbol, "status": "no_data", "detail": None}

    save_index_candles(df)

    print(f"Saved {len(df)} candles for {index_symbol}")

    return {
        "symbol": index_symbol,
        "status": "updated",
        "detail": f"{len(df)} candles, latest={df['date'].max()}",
    }


def update_all_indices():
    results = []

    for index_symbol in set(INDEX_SYMBOLS.values()):
        try:
            result = update_index_history(index_symbol)
        except Exception as e:
            print(f"Failed: {index_symbol} -> {e}")
            result = {"symbol": index_symbol, "status": "error", "detail": str(e)}

        results.append(result)

    return results
