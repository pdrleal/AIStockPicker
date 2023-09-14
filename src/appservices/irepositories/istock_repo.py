import abc
from stockstats import StockDataFrame

class IStockRepo(abc.ABC):
    @abc.abstractmethod
    def get_all(self)->StockDataFrame:
        pass
    def create_stock(self,):
        pass
    def update_stock(self):
        pass
    
    def call_stock_data(self):
        pass
