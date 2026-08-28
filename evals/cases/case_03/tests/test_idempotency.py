from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import process_payment


def test_retry_reuses_original_charge() -> None:
    conn = connect()

    first_charge_id = process_payment(conn, "req-123", 5000)
    retry_charge_id = process_payment(conn, "req-123", 5000)

    count = conn.execute("SELECT COUNT(*) FROM charges").fetchone()[0]

    assert retry_charge_id == first_charge_id
    assert count == 1
