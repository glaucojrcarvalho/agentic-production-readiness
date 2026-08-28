from threading import Barrier, Thread

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


def test_racing_deliveries_return_one_stored_result() -> None:
    store = WebhookStore()
    barrier = Barrier(2)
    results: list[dict] = []

    def worker(kind: str) -> None:
        barrier.wait()
        results.append(handle_webhook(store, "evt-race", {"kind": kind}))

    threads = [
        Thread(target=worker, args=("invoice.paid",)),
        Thread(target=worker, args=("invoice.updated",)),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    stored = store.get("evt-race")
    assert stored is not None
    assert len(results) == 2
    assert results[0] == stored
    assert results[1] == stored
