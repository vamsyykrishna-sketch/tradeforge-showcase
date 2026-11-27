from src.data.database import get_connection
import pandas as pd


def save_index_candles(df):
    conn = get_connection()

    conn.executemany(
        """
        INSERT OR REPLACE INTO index_prices
        (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        df.itertuples(index=False, name=None),
    )

    conn.commit()
    conn.close()


def load_index_candles(symbol):
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM index_prices
        WHERE symbol = ?
        ORDER BY date
        """,
        conn,
        params=(symbol,),
    )

    conn.close()

    return df


def get_latest_index_date(symbol):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT MAX(date)
        FROM index_prices
        WHERE symbol = ?
        """,
        (symbol,),
    )

    latest = cursor.fetchone()[0]

    conn.close()

    return latest
