import abc
from datetime import datetime


class IStockController(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self):
        pass

    @abc.abstractmethod
    def forecast_data(self, request_args: dict):
        pass

    @abc.abstractmethod
    def test_performance(self, request_args: dict):
        pass
