from evals.cases.case_09.src.orders import transition_order


def test_created_order_can_be_paid() -> None:
    order = {"id": 1, "status": "created"}

    assert transition_order(order, "paid")["status"] == "paid"
