import sqlite3


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE idempotency_records (
            request_id TEXT PRIMARY KEY,
            amount_cents INTEGER NOT NULL,
            charge_id INTEGER NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE charges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount_cents INTEGER NOT NULL
        )
        """
    )
    return conn
