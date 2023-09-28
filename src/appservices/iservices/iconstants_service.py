import abc


class IConstantsService(abc.ABC):
    @abc.abstractmethod
    def stocks_indices(self) -> list[str]:
        pass
