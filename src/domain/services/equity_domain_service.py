import pandas as pd
import dataclasses

from src.domain.aggregates.equity import Equity

class EquityDomainService:
    
    # function that maps equity to a dataframe
    @staticmethod
    def map_equity_to_df(equity: Equity):
        
        dates= pd.DatetimeIndex(equity.date_range.timestamps)
        indexSeries = pd.Series(equity.index.index, index=dates)
        pricesSeries= pd.Series(equity.price_list.price_list, index=dates)
        newsSentimentSeries= pd.Series(equity.news_sentiment_list.news_sentiment_list, index=dates)
        socialSentimentSeries= pd.Series(equity.social_sentiment_list.social_sentiment_list, index=dates)
        #dataframe with all series
        dataframe= pd.DataFrame({'index': indexSeries, 'price': pricesSeries, 'news_sentiment': newsSentimentSeries, 'social_sentiment': socialSentimentSeries})
        # return the dataframe
        return dataframe