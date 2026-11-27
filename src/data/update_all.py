from src.data.symbol_repository import get_symbols
from src.data.updater import update_history


def update_all_symbols():
    symbols = get_symbols()

    print(f"Updating {len(symbols)} symbols...")

    results = []

    for i, symbol in enumerate(symbols, start=1):
        print(f"[{i}/{len(symbols)}] {symbol}")

        try:
            result = update_history(symbol)
        except Exception as e:
            print(f"Failed: {symbol} -> {e}")
            result = {"symbol": symbol, "status": "error", "detail": str(e)}

        results.append(result)

    print("Update complete.")

    return results