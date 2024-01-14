import abc


class IStockController(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self):
        pass

    @abc.abstractmethod
    def forecast_data(self):
        pass
