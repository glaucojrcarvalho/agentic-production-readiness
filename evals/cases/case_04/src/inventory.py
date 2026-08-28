import time


class Inventory:
    def __init__(self, stock: dict[str, int]) -> None:
        self._stock = dict(stock)

    def reserve(self, sku: str, quantity: int) -> bool:
        available = self._stock.get(sku, 0)
        if quantity <= 0 or available < quantity:
            return False

        # Simulate work that can occur between reading and persisting state.
        time.sleep(0.01)
        self._stock[sku] = available - quantity
        return True

    def available(self, sku: str) -> int:
        return self._stock.get(sku, 0)
