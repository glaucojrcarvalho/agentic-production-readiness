import pytest

from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import PaymentValidationError, process_payment


@pytest.mark.parametrize(
    ("request_id", "amount_cents"),
    [
        ("", 5000),
        ("   ", 5000),
        (123, 5000),
        ("req-zero", 0),
        ("req-negative", -100),
        ("req-float", 1.5),
        ("req-bool", True),
    ],
)
def test_invalid_payment_input_is_rejected(request_id, amount_cents) -> None:
    conn = connect()

    with pytest.raises(PaymentValidationError):
        process_payment(conn, request_id, amount_cents)

    assert conn.execute("SELECT COUNT(*) FROM charges").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM idempotency_records").fetchone()[0] == 0
