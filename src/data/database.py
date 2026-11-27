import sqlite3
from pathlib import Path

DB_PATH = Path("data/market.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_prices (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY(symbol, date)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS symbols (
            symbol TEXT PRIMARY KEY,
            active INTEGER NOT NULL DEFAULT 1
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS symbol_universe (
            symbol TEXT NOT NULL,
            universe TEXT NOT NULL,
            PRIMARY KEY (symbol, universe)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS symbol_industry (
            symbol   TEXT NOT NULL,
            industry TEXT NOT NULL,
            PRIMARY KEY (symbol)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS index_prices (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY(symbol, date)
        )
    """)

    return conn