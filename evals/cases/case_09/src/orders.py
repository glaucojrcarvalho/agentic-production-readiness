ALLOWED_TRANSITIONS = {
    "created": {"paid", "cancelled"},
    "paid": {"shipped", "cancelled"},
    "shipped": {"delivered"},
    "delivered": set(),
    "cancelled": {"paid"},
}


def transition_order(order: dict, new_status: str) -> dict:
    current = order["status"]
    if new_status not in ALLOWED_TRANSITIONS.get(current, set()):
        raise ValueError(f"invalid transition: {current} -> {new_status}")

    return {**order, "status": new_status}
