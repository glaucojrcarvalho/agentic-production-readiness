import pytest

from evals.cases.case_01.src.db import connect
from evals.cases.case_01.src.orders import create_order


def test_failed_business_operation_leaves_no_partial_state() -> None:
    conn = connect()

    with pytest.raises(RuntimeError, match="simulated audit write failure"):
        create_order(conn, "alice", 2500, fail_audit=True)

    order_count = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
    audit_count = conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

    # Production invariant: the business operation is atomic. This assertion
    # intentionally fails for the planted defect.
    assert order_count == 0
    assert audit_count == 0
