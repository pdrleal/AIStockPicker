import abc
from src.dtos.stock_dto import StockDTO

class IStockService(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self)->list[StockDTO]:
        pass
