from evals.cases.case_04.src.inventory import Inventory


def test_single_reservation_reduces_stock() -> None:
    inventory = Inventory({"sku-1": 3})

    assert inventory.reserve("sku-1", 2) is True
    assert inventory.available("sku-1") == 1
