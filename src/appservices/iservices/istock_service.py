import abc
from stockstats import StockDataFrame

class IStockService(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self)->StockDataFrame:
        pass
