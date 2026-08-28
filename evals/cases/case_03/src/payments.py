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
    """Create one charge per logical request and safely replay duplicates."""
    if not request_id or not request_id.strip():
        raise PaymentValidationError("request_id must be non-empty")
    if amount_cents <= 0:
        raise PaymentValidationError("amount_cents must be positive")

    owns_transaction = not conn.in_transaction
    savepoint = "payment_operation"

    if owns_transaction:
        # Serialize competing writers before the idempotency check so two
        # concurrent requests cannot both observe a missing key.
        conn.execute("BEGIN IMMEDIATE")
    else:
        # Preserve transaction ownership when called from a larger unit of work.
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
            charge_id = int(existing["charge_id"])
        else:
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

        if owns_transaction:
            conn.commit()
        else:
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        return charge_id
    except Exception:
        if owns_transaction:
            conn.rollback()
        else:
            conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
            conn.execute(f"RELEASE SAVEPOINT {savepoint}")
        raise
