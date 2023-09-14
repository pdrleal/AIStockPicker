

from src.interfaceadapters.repositories.stock_repo import StockRepo


def test_init():
    stock_repo=StockRepo()
    assert stock_repo is not None