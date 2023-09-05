import abc

class IEquityRepo(abc.ABC):
    @abc.abstractmethod
    def list(self):
        pass
