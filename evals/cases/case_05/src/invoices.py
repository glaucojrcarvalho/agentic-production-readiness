class InvoiceRepository:
    def __init__(self, invoices: list[dict]) -> None:
        self._invoices = {invoice["id"]: dict(invoice) for invoice in invoices}

    def get(self, invoice_id: int) -> dict | None:
        invoice = self._invoices.get(invoice_id)
        return dict(invoice) if invoice is not None else None


def get_invoice_for_tenant(
    repo: InvoiceRepository,
    invoice_id: int,
    actor_tenant_id: str,
) -> dict | None:
    invoice = repo.get(invoice_id)
    if invoice is None:
        return None

    return invoice
