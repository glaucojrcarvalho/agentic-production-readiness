from evals.cases.case_01.src.db import connect
from evals.cases.case_01.src.orders import create_order


def test_order_and_audit_are_created_on_success() -> None:
    conn = connect()

    order_id = create_order(conn, "alice", 2500)

    order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    audit_count = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

    assert order_id == 1
    assert order_count == 1
    assert audit_count == 1
