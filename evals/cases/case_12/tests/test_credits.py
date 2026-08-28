from evals.cases.case_12.src.credits import CreditLedger, issue_credit


def test_account_can_receive_credit() -> None:
    ledger = CreditLedger()

    entry = issue_credit(
        ledger,
        actor_account_id="acct-a",
        target_account_id="acct-a",
        amount_cents=2500,
        request_id="req-1",
    )

    assert entry["account_id"] == "acct-a"
    assert entry["amount_cents"] == 2500
