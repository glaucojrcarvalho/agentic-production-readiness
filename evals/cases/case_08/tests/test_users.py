from evals.cases.case_08.src.users import UserRepository, list_users_with_order_counts


def test_lists_users_with_order_counts() -> None:
    repo = UserRepository(
        users=[{"id": 1, "name": "Ada"}, {"id": 2, "name": "Linus"}],
        orders=[{"id": 10, "user_id": 1}, {"id": 11, "user_id": 1}],
    )

    assert list_users_with_order_counts(repo) == [
        {"id": 1, "name": "Ada", "order_count": 2},
        {"id": 2, "name": "Linus", "order_count": 0},
    ]
