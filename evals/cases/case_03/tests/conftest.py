import pytest

from evals.cases.case_03.src.db import reset_database


@pytest.fixture(autouse=True)
def _reset_case_database() -> None:
    reset_database()
