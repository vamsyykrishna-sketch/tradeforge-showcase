from src.data.database import get_connection


def add_symbol(symbol):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO symbols (symbol)
        VALUES (?)
        """,
        (symbol,),
    )

    conn.commit()
    conn.close()


def get_symbols():
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT symbol
        FROM symbols
        WHERE active = 1
        ORDER BY symbol
        """
    )

    symbols = [row[0] for row in cursor.fetchall()]

    conn.close()

    return symbols


def deactivate_symbol(symbol):
    conn = get_connection()

    conn.execute(
        """
        UPDATE symbols
        SET active = 0
        WHERE symbol = ?
        """,
        (symbol,),
    )

    conn.commit()
    conn.close()

def symbol_count():
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT COUNT(*)
        FROM symbols
        """
    )

    count = cursor.fetchone()[0]

    conn.close()

    return count

def symbol_exists(symbol):
    conn = get_connection()

    cursor = conn.execute(
        """
        SELECT 1
        FROM symbols
        WHERE symbol = ?
        """,
        (symbol,),
    )

    exists = cursor.fetchone() is not None

    conn.close()

    return exists
def get_active_symbols():
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT symbol
        FROM symbols
        WHERE active = 1
        ORDER BY symbol
        """
    ).fetchall()

    conn.close()

    return [row[0] for row in rows]
def load_symbols() -> list[str]:
    conn = get_connection()

    cursor = conn.execute("""
        SELECT symbol
        FROM symbols
        WHERE active = 1
        ORDER BY symbol
    """)

    symbols = [row[0] for row in cursor.fetchall()]

    conn.close()

    return symbols