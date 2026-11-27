from src.data.database import get_connection
import pandas as pd


def save_candles(df):
    conn = get_connection()

    conn.executemany(
        """
        INSERT OR REPLACE INTO daily_prices
        (symbol, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        df.itertuples(index=False, name=None),
    )

    conn.commit()
    conn.close()


def load_candles(symbol):
    conn = get_connection()

    df = pd.read_sql_query(
        """
        SELECT *
        FROM daily_prices
        WHERE symbol = ?
        ORDER BY date
        """,
        conn,
        params=(symbol,),
    )

    conn.close()

    return df


def get_global_latest_date():
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT MAX(date)
        FROM daily_prices
        """
    )

    latest = cursor.fetchone()[0]

    conn.close()

    return latest


def get_latest_date(symbol):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT MAX(date)
        FROM daily_prices
        WHERE symbol = ?
        """,
        (symbol,),
    )

    latest = cursor.fetchone()[0]

    conn.close()

    return latest

def delete_symbol_prices(symbol):
    conn = get_connection()

    conn.execute(
        """
        DELETE FROM daily_prices
        WHERE symbol = ?
        """,
        (symbol,),
    )

    conn.commit()
    conn.close()