import pytest

from src.db import connect
from src.payments import IdempotencyConflict, process_payment


def test_same_key_with_different_payload_is_rejected() -> None:
    conn = connect()

    first_charge_id = process_payment(conn, "req-123", 5000)

    with pytest.raises(IdempotencyConflict):
        process_payment(conn, "req-123", 7000)

    rows = conn.execute(
        "SELECT id, amount_cents FROM charges ORDER BY id"
    ).fetchall()

    assert [(row["id"], row["amount_cents"]) for row in rows] == [
        (first_charge_id, 5000)
    ]
