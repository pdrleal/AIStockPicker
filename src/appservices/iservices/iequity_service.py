import abc

class IEquityService(abc.ABC):
    @abc.abstractmethod
    def list(self):
        pass
