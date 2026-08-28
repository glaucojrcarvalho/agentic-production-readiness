import sqlite3


_DATABASE_URI = "file:case03_clean_control?mode=memory&cache=shared"


def _new_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(
        _DATABASE_URI,
        uri=True,
        timeout=5.0,
        isolation_level=None,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    return conn


# Keep one connection open so the shared in-memory database survives across
# independent connections for the lifetime of the process.
_KEEPER = _new_connection()
_KEEPER.executescript(
    """
    CREATE TABLE IF NOT EXISTS charges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount_cents INTEGER NOT NULL CHECK (amount_cents > 0)
    );

    CREATE TABLE IF NOT EXISTS idempotency_records (
        request_id TEXT PRIMARY KEY CHECK (length(trim(request_id)) > 0),
        amount_cents INTEGER NOT NULL CHECK (amount_cents > 0),
        charge_id INTEGER,
        FOREIGN KEY (charge_id) REFERENCES charges(id)
    );
    """
)


def connect() -> sqlite3.Connection:
    """Return a connection to the shared case database."""
    return _new_connection()


def reset_database() -> None:
    """Reset shared state between tests while keeping connection semantics intact."""
    _KEEPER.execute("DELETE FROM idempotency_records")
    _KEEPER.execute("DELETE FROM charges")
    _KEEPER.execute("DELETE FROM sqlite_sequence WHERE name = 'charges'")
