from evals.cases.case_05.src.invoices import InvoiceRepository, get_invoice_for_tenant


def test_owner_can_read_invoice() -> None:
    repo = InvoiceRepository([
        {"id": 7, "tenant_id": "tenant-a", "amount_cents": 1200},
    ])

    invoice = get_invoice_for_tenant(repo, 7, "tenant-a")

    assert invoice is not None
    assert invoice["amount_cents"] == 1200
