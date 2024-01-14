import abc

import pandas as pd


class IStockService(abc.ABC):
    @abc.abstractmethod
    def refresh_data(self) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def forecast_data(self) -> pd.DataFrame:
        pass
