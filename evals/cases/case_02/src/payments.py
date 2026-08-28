import sqlite3


def process_payment(
    conn: sqlite3.Connection,
    request_id: str,
    amount_cents: int,
) -> int:
    """Record a payment side effect for one request.

    This fixture intentionally ignores prior use of request_id. Retrying the
    same logical request therefore creates another charge.
    """
    cursor = conn.execute(
        "INSERT INTO charges (request_id, amount_cents) VALUES (?, ?)",
        (request_id, amount_cents),
    )
    conn.commit()
    return int(cursor.lastrowid)
