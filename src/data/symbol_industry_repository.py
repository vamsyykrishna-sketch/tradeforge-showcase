from src.data.database import get_connection


def add_symbol_industry(symbol: str, industry: str):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO symbol_industry (symbol, industry)
        VALUES (?, ?)
        """,
        (symbol, industry),
    )

    conn.commit()
    conn.close()


def get_industry_for_symbol(symbol: str) -> str | None:
    conn = get_connection()

    row = conn.execute(
        """
        SELECT industry
        FROM symbol_industry
        WHERE symbol = ?
        """,
        (symbol,),
    ).fetchone()

    conn.close()

    return row[0] if row else None


def get_all_symbol_industries() -> dict[str, str]:
    """Bulk symbol -> industry map, one query for the whole table — same
    convention as symbol_universe_repository.py's get_all_symbol_universes(),
    for callers (e.g. sector RS aggregation, a UI rendering hundreds of rows)
    that would otherwise need get_industry_for_symbol() once per symbol."""
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT symbol, industry
        FROM symbol_industry
        ORDER BY symbol
        """
    ).fetchall()

    conn.close()

    return {symbol: industry for symbol, industry in rows}
