from src.data.database import get_connection


def add_symbol_universe(symbol: str, universe: str):
    conn = get_connection()

    conn.execute(
        """
        INSERT OR IGNORE INTO symbol_universe (symbol, universe)
        VALUES (?, ?)
        """,
        (symbol, universe),
    )

    conn.commit()
    conn.close()


def get_universes_for_symbol(symbol: str) -> list[str]:
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT universe
        FROM symbol_universe
        WHERE symbol = ?
        ORDER BY universe
        """,
        (symbol,),
    ).fetchall()

    conn.close()

    return [row[0] for row in rows]


def get_all_symbol_universes() -> dict[str, list[str]]:
    """Bulk symbol -> [universe, ...] map, one query for the whole table —
    for callers (e.g. a UI rendering hundreds of rows) that would otherwise
    need get_universes_for_symbol() once per symbol."""
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT symbol, universe
        FROM symbol_universe
        ORDER BY symbol, universe
        """
    ).fetchall()

    conn.close()

    result: dict[str, list[str]] = {}
    for symbol, universe in rows:
        result.setdefault(symbol, []).append(universe)

    return result


def get_all_universes() -> list[str]:
    """Distinct universe names present in the table, for populating a
    universe filter's option list."""
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT DISTINCT universe
        FROM symbol_universe
        ORDER BY universe
        """
    ).fetchall()

    conn.close()

    return [row[0] for row in rows]
