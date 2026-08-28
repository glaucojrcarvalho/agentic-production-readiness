from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier, Thread
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def verify_case_04() -> None:
    from evals.cases.case_04.src.inventory import Inventory

    inventory = Inventory({"sku-1": 1})
    barrier = Barrier(2)
    original_available = inventory.available

    results: list[bool] = []

    def worker() -> None:
        barrier.wait()
        results.append(inventory.reserve("sku-1", 1))

    threads = [Thread(target=worker), Thread(target=worker)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count(True) == 2, results
    assert original_available("sku-1") == 0


def verify_case_05() -> None:
    from evals.cases.case_05.src.invoices import InvoiceRepository, get_invoice_for_tenant

    repo = InvoiceRepository([
        {"id": 7, "tenant_id": "tenant-a", "amount_cents": 1200},
    ])
    leaked = get_invoice_for_tenant(repo, 7, "tenant-b")
    assert leaked is not None
    assert leaked["tenant_id"] == "tenant-a"


def verify_case_06() -> None:
    from evals.cases.case_06.src.retry import call_with_retry

    calls = 0

    def operation() -> None:
        nonlocal calls
        calls += 1
        raise ValueError("invalid request")

    try:
        call_with_retry(operation)
    except ValueError:
        pass
    else:
        raise AssertionError("ValueError should propagate")

    assert calls == 3, calls


def verify_case_07() -> None:
    from evals.cases.case_07.src.jobs import run_job

    def handler() -> None:
        raise RuntimeError("write failed")

    result = run_job(handler)
    assert result == {"status": "ok", "result": None}


def verify_case_08() -> None:
    from evals.cases.case_08.src.users import UserRepository, list_users_with_order_counts

    class CountingRepository(UserRepository):
        def __init__(self) -> None:
            users = [{"id": i, "name": f"user-{i}"} for i in range(100)]
            orders = [{"id": i, "user_id": i} for i in range(100)]
            super().__init__(users, orders)
            self.calls = 0

        def list_users(self) -> list[dict]:
            self.calls += 1
            return super().list_users()

        def orders_for_user(self, user_id: int) -> list[dict]:
            self.calls += 1
            return super().orders_for_user(user_id)

    repo = CountingRepository()
    result = list_users_with_order_counts(repo)
    assert len(result) == 100
    assert repo.calls == 101, repo.calls


def verify_case_09() -> None:
    from evals.cases.case_09.src.orders import transition_order

    cancelled = {"id": 1, "status": "cancelled"}
    transitioned = transition_order(cancelled, "paid")
    assert transitioned["status"] == "paid"


def verify_case_10() -> None:
    from evals.cases.case_10.src.tokens import is_token_expired

    expires = datetime(2026, 8, 28, 12, 0, tzinfo=timezone.utc)
    now = datetime(2026, 8, 28, 8, 30, tzinfo=timezone(timedelta(hours=-4)))

    assert now.astimezone(timezone.utc) > expires
    assert is_token_expired(expires, now) is False


def verify_case_11() -> None:
    from evals.cases.case_11.src.webhooks import WebhookStore, handle_webhook

    store = WebhookStore()
    first = handle_webhook(store, "evt-1", {"kind": "invoice.paid"})
    second = handle_webhook(store, "evt-1", {"kind": "different.payload"})
    assert second == first

    try:
        handle_webhook(store, "", {"kind": "invoice.paid"})
    except ValueError:
        pass
    else:
        raise AssertionError("empty event_id must be rejected")


def verify_case_12() -> None:
    from evals.cases.case_12.src.credits import CreditLedger, issue_credit

    ledger = CreditLedger()
    unauthorized = issue_credit(
        ledger,
        actor_account_id="acct-a",
        target_account_id="acct-b",
        amount_cents=2500,
        request_id="req-1",
    )
    assert unauthorized["account_id"] == "acct-b"

    issue_credit(ledger, "acct-a", "acct-a", 2500, "req-repeat")
    issue_credit(ledger, "acct-a", "acct-a", 2500, "req-repeat")
    repeated = [entry for entry in ledger.entries if entry["request_id"] == "req-repeat"]
    assert len(repeated) == 2


VERIFIERS = {
    "case_04": verify_case_04,
    "case_05": verify_case_05,
    "case_06": verify_case_06,
    "case_07": verify_case_07,
    "case_08": verify_case_08,
    "case_09": verify_case_09,
    "case_10": verify_case_10,
    "case_11": verify_case_11,
    "case_12": verify_case_12,
}


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in VERIFIERS:
        raise SystemExit(f"usage: python evals/verify_cases.py <{'|'.join(VERIFIERS)}>")
    VERIFIERS[sys.argv[1]]()
    print(f"{sys.argv[1]} verification passed")
