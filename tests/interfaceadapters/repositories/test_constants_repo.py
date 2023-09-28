from src.interfaceadapters.repositories.constants_repo import ConstantsRepo


def test_stocks_list_length():
    repository = ConstantsRepo()
    stocks_indices = repository.get_stocks_indices()
    assert len(stocks_indices) > 0
