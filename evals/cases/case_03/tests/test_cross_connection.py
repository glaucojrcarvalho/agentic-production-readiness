from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import process_payment


def test_retry_on_another_connection_reuses_original_charge() -> None:
    first_conn = connect()
    second_conn = connect()

    first_charge_id = process_payment(first_conn, "req-cross-connection", 5000)
    retry_charge_id = process_payment(second_conn, "req-cross-connection", 5000)

    count = second_conn.execute("SELECT COUNT(*) FROM charges").fetchone()[0]

    assert retry_charge_id == first_charge_id
    assert count == 1
