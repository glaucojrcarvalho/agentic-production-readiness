import sqlite3


def create_order(
    conn: sqlite3.Connection,
    customer: str,
    total_cents: int,
    *,
    fail_audit: bool = False,
) -> int:
    """Create an order and its audit record.

    This fixture intentionally contains a production-readiness defect:
    the order is committed before the audit write, so a later failure
    can leave partial persisted state.
    """
    cursor = conn.execute(
        "INSERT INTO orders (customer, total_cents) VALUES (?, ?)",
        (customer, total_cents),
    )
    order_id = int(cursor.lastrowid)

    # Defect: the first half of the business operation is made durable
    # before the second half succeeds.
    conn.commit()

    if fail_audit:
        raise RuntimeError("simulated audit write failure")

    conn.execute(
        "INSERT INTO audit_log (order_id, event) VALUES (?, ?)",
        (order_id, "order_created"),
    )
    conn.commit()
    return order_id
