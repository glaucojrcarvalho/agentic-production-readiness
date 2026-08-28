from evals.cases.case_07.src.jobs import run_job


def test_successful_job_returns_result() -> None:
    assert run_job(lambda: 42) == {"status": "ok", "result": 42}
