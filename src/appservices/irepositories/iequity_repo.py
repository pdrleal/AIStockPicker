import abc

from src.domain.aggregates.equity import Equity

class IEquityRepo(abc.ABC):
    @abc.abstractmethod
    def get_all(self)->list[Equity]:
        pass
    def add_stock_data(self):
        pass
    def update_stock_data(self):
        pass
