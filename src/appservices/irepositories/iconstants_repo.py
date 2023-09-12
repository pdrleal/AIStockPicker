import abc

class IConstantsRepo(abc.ABC):
    @abc.abstractmethod
    def stocks_indices(self)->list[str]:
        pass
