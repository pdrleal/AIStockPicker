import abc
from src.dtos.equity_dto import EquityDTO

class IEquityService(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self)->list[EquityDTO]:
        pass
