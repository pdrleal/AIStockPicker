from src.appservices.stock_service import StockService
from src.interfaceadapters.repositories.constants_repo import ConstantsRepo
from src.interfaceadapters.repositories.stock_repo import StockRepo

constants_repo = ConstantsRepo()
stock_repo = StockRepo()
stock_service = StockService(constants_repo, stock_repo)


def test_init():
    assert stock_service is not None


def test_clean_landing_data():
    stock_service.clean_landing_data()
