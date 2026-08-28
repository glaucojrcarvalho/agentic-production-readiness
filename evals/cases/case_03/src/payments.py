import sqlite3


class IdempotencyConflict(ValueError):
    pass


class PaymentValidationError(ValueError):
    pass


class TransactionOwnershipError(RuntimeError):
    pass


def process_payment(
    conn: sqlite3.Connection,
    request_id: str,
    amount_cents: int,
) -> int:
    """Create one charge per logical request using a transaction owned here."""
    if not isinstance(request_id, str) or not request_id.strip():
        raise PaymentValidationError("request_id must be a non-empty string")
    if (
        not isinstance(amount_cents, int)
        or isinstance(amount_cents, bool)
        or amount_cents <= 0
    ):
        raise PaymentValidationError("amount_cents must be a positive integer")
    if conn.in_transaction:
        raise TransactionOwnershipError(
            "process_payment requires a connection with no active transaction"
        )

    # Acquire the write reservation before the idempotency read so competing
    # requests cannot both observe a missing key and then race to insert.
    conn.execute("BEGIN IMMEDIATE")

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

        conn.commit()
        return charge_id
    except Exception:
        conn.rollback()
        raise
