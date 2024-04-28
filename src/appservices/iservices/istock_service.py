import abc
from datetime import datetime
import pandas as pd


class IStockService(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def forecast_data(self, stock_index: str, current_date: datetime):
        pass

    @abc.abstractmethod
    def build_portfolio(self, current_date: datetime):
        pass

    @abc.abstractmethod
    def test_performance(self, start_date: datetime, end_date: datetime):
        pass
