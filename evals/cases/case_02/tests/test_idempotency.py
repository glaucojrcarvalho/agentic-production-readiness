from src.db import connect
from src.payments import process_payment


def test_retry_does_not_duplicate_business_side_effect() -> None:
    conn = connect()

    first_charge_id = process_payment(conn, "req-123", 5000)
    retry_charge_id = process_payment(conn, "req-123", 5000)

    count = conn.execute(
        "SELECT COUNT(*) FROM charges WHERE request_id = ?", ("req-123",)
    ).fetchone()[0]

    # Production invariant: a retry of the same logical request must reuse the
    # original outcome rather than create a second side effect. These
    # assertions intentionally fail for the planted defect.
    assert count == 1
    assert retry_charge_id == first_charge_id
