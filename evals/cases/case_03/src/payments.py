import sqlite3


class IdempotencyConflict(ValueError):
    pass


class PaymentValidationError(ValueError):
    pass


def process_payment(
    conn: sqlite3.Connection,
    request_id: str,
    amount_cents: int,
) -> int:
    """Create one charge per logical request and safely replay duplicates.

    The function preserves caller transaction ownership by using a savepoint.
    The idempotency reservation is created before the side effect so concurrent
    callers converge on one durable outcome.
    """
    if not request_id or not request_id.strip():
        raise PaymentValidationError("request_id must be non-empty")
    if amount_cents <= 0:
        raise PaymentValidationError("amount_cents must be positive")

    savepoint = "payment_operation"
    conn.execute(f"SAVEPOINT {savepoint}")

    try:
        existing = conn.execute(
            "SELECT amount_cents, charge_id FROM idempotency_records WHERE request_id = ?",
            (request_id,),
        ).fetchone()

        if existing is not None:
            if existing["amount_cents"] != amount_cents:
                raise IdempotencyConflict(
                    "idempotency key was already used with different request data"
                )
            if existing["charge_id"] is None:
                raise RuntimeError("idempotency record has no completed charge")
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
            return int(existing["charge_id"])

        reservation = conn.execute(
            """
            INSERT OR IGNORE INTO idempotency_records (request_id, amount_cents, charge_id)
            VALUES (?, ?, NULL)
            """,
            (request_id, amount_cents),
        )

        if reservation.rowcount == 0:
            winner = conn.execute(
                "SELECT amount_cents, charge_id FROM idempotency_records WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            if winner is None or winner["charge_id"] is None:
                raise RuntimeError("concurrent idempotency reservation did not complete")
            if winner["amount_cents"] != amount_cents:
                raise IdempotencyConflict(
                    "idempotency key was already used with different request data"
                )
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
            return int(winner["charge_id"])

        cursor = conn.execute(
            "INSERT INTO charges (amount_cents) VALUES (?)",
            (amount_cents,),
        )
        charge_id = int(cursor.lastrowid)
        conn.execute(
            """
            UPDATE idempotency_records
            SET charge_id = ?
            WHERE request_id = ?
            """,
            (charge_id, request_id),
        )
        conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        return charge_id
    except Exception:
        conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
        conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        raise
