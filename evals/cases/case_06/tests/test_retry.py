from evals.cases.case_06.src.retry import call_with_retry


def test_transient_failure_can_recover() -> None:
    calls = 0

    def operation() -> str:
        nonlocal calls
        calls += 1
        if calls < 2:
            raise TimeoutError("temporary")
        return "ok"

    assert call_with_retry(operation) == "ok"
    assert calls == 2
