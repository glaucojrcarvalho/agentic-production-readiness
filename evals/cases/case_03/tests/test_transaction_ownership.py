from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import process_payment


def test_payment_preserves_caller_owned_transaction() -> None:
    conn = connect()
    conn.execute("CREATE TABLE IF NOT EXISTS caller_work (value TEXT NOT NULL)")
    conn.execute("DELETE FROM caller_work")

    conn.execute("BEGIN")
    conn.execute("INSERT INTO caller_work (value) VALUES ('keep-me')")

    charge_id = process_payment(conn, "req-nested", 5000)

    assert conn.in_transaction is True
    assert conn.execute("SELECT COUNT(*) FROM caller_work").fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM charges WHERE id = ?", (charge_id,)).fetchone()[0] == 1

    conn.rollback()

    assert conn.execute("SELECT COUNT(*) FROM caller_work").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM charges WHERE id = ?", (charge_id,)).fetchone()[0] == 0
