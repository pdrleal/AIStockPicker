import abc

class IEquityController(abc.ABC):
    @abc.abstractmethod
    def equity_list(self):
        pass