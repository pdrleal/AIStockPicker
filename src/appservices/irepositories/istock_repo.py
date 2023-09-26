import abc
import pandas as pd
class IStockRepo(abc.ABC):
    @abc.abstractmethod
    def get_all(self)->pd.DataFrame:
        pass
    def create_stock(self,):
        pass
    def update_stock(self):
        pass

    def call_stock_data(self):
        pass
