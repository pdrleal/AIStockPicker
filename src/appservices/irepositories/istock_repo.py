import abc

from src.domain.aggregates.stock import Stock

class IStockRepo(abc.ABC):
    @abc.abstractmethod
    def get_all(self)->list[Stock]:
        pass
    def create_stock(self,):
        pass
    def update_stock(self):
        pass
    
    def call_stock_data(self):
        pass
