import abc

class IEquityController(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self):
        pass