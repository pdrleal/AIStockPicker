import abc
import pandas as pd


class IStockRepo(abc.ABC):
    @abc.abstractmethod
    def add_landing_stock_prices(self):
        pass

    @abc.abstractmethod
    def add_landing_news_sentiments(self):
        pass

    @abc.abstractmethod
    def add_landing_social_sentiments(self):
        pass

    @abc.abstractmethod
    def get_landing_stock_prices(self) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_landing_news_sentiments(self) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_landing_social_sentiments(self) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def add_batch_clean(self, clean_df: pd.DataFrame):
        pass
