class UserRepository:
    def __init__(self, users: list[dict], orders: list[dict]) -> None:
        self._users = list(users)
        self._orders = list(orders)

    def list_users(self) -> list[dict]:
        return [dict(user) for user in self._users]

    def orders_for_user(self, user_id: int) -> list[dict]:
        return [dict(order) for order in self._orders if order["user_id"] == user_id]


def list_users_with_order_counts(repo: UserRepository) -> list[dict]:
    result = []
    for user in repo.list_users():
        orders = repo.orders_for_user(user["id"])
        result.append({**user, "order_count": len(orders)})
    return result
