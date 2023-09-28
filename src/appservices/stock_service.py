import json

import pandas as pd

from src.appservices.irepositories.iconstants_repo import IConstantsRepo
from src.appservices.irepositories.istock_repo import IStockRepo
from src.appservices.iservices.istock_service import IStockService


class StockService(IStockService):

    def __init__(self, constants_repo: IConstantsRepo, stock_repo: IStockRepo):
        self.constants_repo = constants_repo
        self.stock_repo = stock_repo
        self.stocks_indices = self.constants_repo.get_stocks_indices()

    def clean_landing_data(self):
        landing_stock_prices = self.stock_repo.get_landing_stock_prices()

        df_list = []  # Initialize an empty list to store DataFrames
        for index, row in landing_stock_prices.iterrows():
            _, time_series_values = list(row["content"].items())[1]
            df_list.append(pd.DataFrame(time_series_values).T)

        clean_stock_prices = pd.concat(df_list)
        clean_stock_prices.columns = ["date", "open", "high", "low", "close", "volume"]

        #landing_news_sentiments = self.stock_repo.get_landing_news_sentiments()
        #landing_social_sentiments = self.stock_repo.get_landing_social_sentiments()



        return raw_dataframe

    def refresh_data(self):
        #retrieve stock indices from constants_service
        stock_indices=self.constants_service.stocks_indices()

        #retrieve stock data from stock_repo
        raw_dataframe= self.stock_repo.get_all()

        #self.perform_refresh(stock_indices, stock_dto_list)

        return raw_dataframe

    #def perform_refresh(self,stock_indices, stock_dto_list):
    #    for stock_index in stock_indices:
    #        if stock_index not in stock_dto_list:
    #            self.stock_repo.call_stock_data(stock_index)
    #        else:
    #            self.update_stock(stock_index)
    #    pass

    """
     def get_stock(self, stock_id):
        return self.stock_repository.get_stock_by_id(stock_id)

    def get_equities(self):
        return self.stock_repository.get_equities()

    def create_stock(self, stock):
        return self.stock_repository.create_stock(stock)

    def update_stock(self, stock_id, stock):
        return self.stock_repository.update_stock(stock_id, stock)

    def delete_stock(self, stock_id):
        return self.stock_repository.delete_stock(stock_id)
    """
