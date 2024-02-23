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
    def get_landing_stock_prices(self, min_date=None) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_landing_news_sentiments(self, min_date=None) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def get_landing_social_sentiments(self, min_date=None) -> pd.DataFrame:
        pass

    @abc.abstractmethod
    def append_to_clean_table(self, clean_df: pd.DataFrame):
        pass

    @abc.abstractmethod
    def replace_clean_table_by(self, clean_df: pd.DataFrame):
        pass

    @abc.abstractmethod
    def get_clean_stock_prices(self) -> pd.DataFrame:
        pass
