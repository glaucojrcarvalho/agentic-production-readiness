import json
import subprocess
import sys

from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import process_payment


def test_idempotency_survives_separate_process() -> None:
    conn = connect()
    first_charge_id = process_payment(conn, "req-process", 4200)
    conn.close()

    script = """
import json
from evals.cases.case_03.src.db import connect
from evals.cases.case_03.src.payments import process_payment

conn = connect()
charge_id = process_payment(conn, 'req-process', 4200)
count = conn.execute('SELECT COUNT(*) FROM charges').fetchone()[0]
print(json.dumps({'charge_id': charge_id, 'count': count}))
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(completed.stdout.strip())

    assert result["charge_id"] == first_charge_id
    assert result["count"] == 1
