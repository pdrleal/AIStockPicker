from src.domain.aggregates.equity import Equity
from src.appservices.irepositories.iequity_repo import IEquityRepo

class EquityRepo(IEquityRepo):
    
    def __init__(self):
        pass
      
    def get_all(self):
        eq1= Equity.from_start_end_dates(
            index="AAPL",
            start_date="2021-01-01",
            end_date="2021-01-02",
            price_list=[1, 2],
            news_sentiment_list=[1, 2],
            social_sentiment_list=[1, 2],
        )
        eq2= Equity.from_start_end_dates(
            index="AMZN",
            start_date="2021-01-01",
            end_date="2021-01-02",
            price_list=[1, 2],
            news_sentiment_list=[1, 2],
            social_sentiment_list=[1, 2],
        )
        return [eq1, eq2]