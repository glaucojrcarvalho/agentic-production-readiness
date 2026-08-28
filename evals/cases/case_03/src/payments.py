import sqlite3


class IdempotencyConflict(ValueError):
    pass


def process_payment(
    conn: sqlite3.Connection,
    request_id: str,
    amount_cents: int,
) -> int:
    """Create one charge per logical request and safely replay duplicates."""
    existing = conn.execute(
        "SELECT amount_cents, charge_id FROM idempotency_records WHERE request_id = ?",
        (request_id,),
    ).fetchone()

    if existing is not None:
        if existing["amount_cents"] != amount_cents:
            raise IdempotencyConflict(
                "idempotency key was already used with different request data"
            )
        return int(existing["charge_id"])

    try:
        conn.execute("BEGIN")
        cursor = conn.execute(
            "INSERT INTO charges (amount_cents) VALUES (?)",
            (amount_cents,),
        )
        charge_id = int(cursor.lastrowid)
        conn.execute(
            """
            INSERT INTO idempotency_records (request_id, amount_cents, charge_id)
            VALUES (?, ?, ?)
            """,
            (request_id, amount_cents, charge_id),
        )
        conn.commit()
        return charge_id
    except Exception:
        conn.rollback()
        raise
