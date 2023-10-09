from src.interfaceadapters.repositories.constants_repo import ConstantsRepo


def test_stocks_list_length():
    repository = ConstantsRepo()
    stocks_indices = repository.get_stocks_indices()
    assert len(stocks_indices) > 0


def test_constant_by_key():
    repository = ConstantsRepo()
    last_update_date = repository.get_by_key('Last Update Date')
    assert len(last_update_date) > 0
