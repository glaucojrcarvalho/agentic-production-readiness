from pathlib import Path
import sqlite3
import tempfile


_DATABASE_PATH = Path(tempfile.gettempdir()) / "agentic_production_readiness_case03.sqlite3"


def _new_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(
        _DATABASE_PATH,
        timeout=5.0,
        isolation_level=None,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 5000")
    return conn


def _initialize_database() -> None:
    with _new_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS charges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount_cents INTEGER NOT NULL CHECK (
                    typeof(amount_cents) = 'integer' AND amount_cents > 0
                )
            );

            CREATE TABLE IF NOT EXISTS idempotency_records (
                request_id TEXT PRIMARY KEY CHECK (length(trim(request_id)) > 0),
                amount_cents INTEGER NOT NULL CHECK (
                    typeof(amount_cents) = 'integer' AND amount_cents > 0
                ),
                charge_id INTEGER NOT NULL,
                FOREIGN KEY (charge_id) REFERENCES charges(id)
            );
            """
        )


def connect() -> sqlite3.Connection:
    """Return a connection to the persistent local database used by this case."""
    _initialize_database()
    return _new_connection()


def reset_database() -> None:
    """Reset shared state between tests without changing production lifecycle semantics."""
    _initialize_database()
    with _new_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM idempotency_records")
        conn.execute("DELETE FROM charges")
        conn.execute("DELETE FROM sqlite_sequence WHERE name = 'charges'")
        conn.commit()


_initialize_database()
