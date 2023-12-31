import abc


class IConstantsRepo(abc.ABC):
    @abc.abstractmethod
    def get_stocks_indices(self) -> list[str]:
        pass

    @abc.abstractmethod
    def get_by_key(self, key) -> str:
        pass
