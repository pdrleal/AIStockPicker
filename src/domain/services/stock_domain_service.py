import pandas as pd
import dataclasses

from src.domain.aggregates.stock import Stock

class StockDomainService:
    
    # function that maps stock to a dataframe
    @staticmethod
    def map_stock_to_df(stock: Stock):
        
        dates= pd.DatetimeIndex(stock.date_range.timestamps)
        indexSeries = pd.Series(stock.index.index, index=dates)
        pricesSeries= pd.Series(stock.price_list.price_list, index=dates)
        newsSentimentSeries= pd.Series(stock.news_sentiment_list.news_sentiment_list, index=dates)
        socialSentimentSeries= pd.Series(stock.social_sentiment_list.social_sentiment_list, index=dates)
        #dataframe with all series
        dataframe= pd.DataFrame({'index': indexSeries, 'price': pricesSeries, 'news_sentiment': newsSentimentSeries, 'social_sentiment': socialSentimentSeries})
        # return the dataframe
        return dataframe