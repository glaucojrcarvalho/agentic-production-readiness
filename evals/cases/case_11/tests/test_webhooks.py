from evals.cases.case_11.src.webhooks import WebhookStore, handle_webhook


def test_first_delivery_is_accepted() -> None:
    store = WebhookStore()

    assert handle_webhook(store, "evt-1", {"kind": "invoice.paid"}) == {
        "accepted": True,
        "kind": "invoice.paid",
    }


def test_replay_returns_same_result() -> None:
    store = WebhookStore()
    first = handle_webhook(store, "evt-1", {"kind": "invoice.paid"})
    second = handle_webhook(store, "evt-1", {"kind": "invoice.paid"})

    assert second == first
