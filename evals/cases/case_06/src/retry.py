from collections.abc import Callable


def call_with_retry(operation: Callable[[], object], attempts: int = 3) -> object:
    last_error: Exception | None = None

    for _ in range(attempts):
        try:
            return operation()
        except Exception as exc:
            last_error = exc

    assert last_error is not None
    raise last_error
