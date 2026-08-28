from src.db import connect
from src.payments import process_payment


def test_single_request_creates_one_charge() -> None:
    conn = connect()

    charge_id = process_payment(conn, "req-123", 5000)

    count = conn.execute("SELECT COUNT(*) FROM charges").fetchone()[0]

    assert charge_id == 1
    assert count == 1
