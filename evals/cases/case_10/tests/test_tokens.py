from datetime import datetime, timezone

from evals.cases.case_10.src.tokens import is_token_expired


def test_expiration_in_same_timezone() -> None:
    now = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
    expires = datetime(2026, 8, 28, 12, 5, tzinfo=timezone.utc)

    assert is_token_expired(expires, now) is False
