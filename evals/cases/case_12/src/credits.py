class CreditLedger:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def add(self, account_id: str, amount_cents: int, request_id: str) -> dict:
        entry = {
            "id": len(self.entries) + 1,
            "account_id": account_id,
            "amount_cents": amount_cents,
            "request_id": request_id,
        }
        self.entries.append(entry)
        return dict(entry)


def issue_credit(
    ledger: CreditLedger,
    actor_account_id: str,
    target_account_id: str,
    amount_cents: int,
    request_id: str,
) -> dict:
    if amount_cents <= 0:
        raise ValueError("amount_cents must be positive")

    return ledger.add(target_account_id, amount_cents, request_id)
