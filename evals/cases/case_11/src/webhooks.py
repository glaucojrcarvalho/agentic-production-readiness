class DuplicateEvent(Exception):
    pass


class WebhookStore:
    def __init__(self) -> None:
        self._results: dict[str, dict] = {}

    def get(self, event_id: str) -> dict | None:
        result = self._results.get(event_id)
        return dict(result) if result is not None else None

    def save(self, event_id: str, result: dict) -> None:
        if event_id in self._results:
            raise DuplicateEvent(event_id)
        self._results[event_id] = dict(result)


def handle_webhook(store: WebhookStore, event_id: str, payload: dict) -> dict:
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("event_id must be non-empty")

    existing = store.get(event_id)
    if existing is not None:
        return existing

    result = {"accepted": True, "kind": payload.get("kind")}

    try:
        store.save(event_id, result)
    except DuplicateEvent:
        replay = store.get(event_id)
        if replay is None:
            raise
        return replay

    return result
