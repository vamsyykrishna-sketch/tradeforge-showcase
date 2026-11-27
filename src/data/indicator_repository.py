import pandas as pd

from src.data.database import get_connection


def load_prices(symbol: str) -> pd.DataFrame:
    conn = get_connection()

    query = """
        SELECT
            date,
            open,
            high,
            low,
            close,
            volume
        FROM daily_prices
        WHERE symbol = ?
        ORDER BY date
    """

    df = pd.read_sql(query, conn, params=[symbol])

    conn.close()

    df["date"] = pd.to_datetime(df["date"])

    return df