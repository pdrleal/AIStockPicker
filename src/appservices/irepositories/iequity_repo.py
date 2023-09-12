import abc

from src.domain.aggregates.equity import Equity

class IEquityRepo(abc.ABC):
    @abc.abstractmethod
    def get_all(self)->list[Equity]:
        pass
    def create_equity(self,):
        pass
    def update_equity(self):
        pass
    
    def call_equity_data(self):
        pass
