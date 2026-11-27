from pathlib import Path

import pandas as pd


ASSETS_DIR = Path("assets/indices")


def load_index(index_name: str) -> list[tuple[str, str]]:
    """Returns (symbol, industry) pairs -- Industry is NSE's own sector/
    industry classification, already present in every assets/indices/*.csv
    (Company Name,Industry,Symbol,Series,ISIN Code) but previously discarded
    here. No new data source needed for sector RS -- see conversation."""
    file_path = ASSETS_DIR / f"{index_name}.csv"

    df = pd.read_csv(file_path)

    symbols = (
        "NSE:"
        + df["Symbol"].str.strip()
        + "-"
        + df["Series"].str.strip()
    )

    industries = df["Industry"].str.strip()

    return list(zip(symbols, industries))