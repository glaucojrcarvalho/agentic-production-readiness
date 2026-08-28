from src.db import connect
from src.payments import process_payment


def test_single_request_creates_one_charge() -> None:
    conn = connect()

    charge_id = process_payment(conn, "req-123", 5000)

    count = conn.execute("SELECT COUNT(*) FROM charges").fetchone()[0]
    amount = conn.execute(
        "SELECT amount_cents FROM charges WHERE id = ?", (charge_id,)
    ).fetchone()[0]

    assert count == 1
    assert amount == 5000
