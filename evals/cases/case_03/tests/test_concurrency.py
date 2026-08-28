from concurrent.futures import ThreadPoolExecutor
import threading

from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import process_payment


def test_concurrent_duplicate_requests_converge_on_one_charge() -> None:
    barrier = threading.Barrier(2)

    def invoke() -> int:
        conn = connect()
        barrier.wait()
        return process_payment(conn, "req-concurrent", 5000)

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(invoke)
        second = executor.submit(invoke)
        first_charge_id = first.result(timeout=10)
        second_charge_id = second.result(timeout=10)

    check_conn = connect()
    count = check_conn.execute("SELECT COUNT(*) FROM charges").fetchone()[0]

    assert first_charge_id == second_charge_id
    assert count == 1
