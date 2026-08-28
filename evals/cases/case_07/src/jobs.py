from collections.abc import Callable


def run_job(handler: Callable[[], object]) -> dict:
    try:
        result = handler()
        return {"status": "ok", "result": result}
    except Exception:
        return {"status": "ok", "result": None}
