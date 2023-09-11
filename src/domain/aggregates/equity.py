import uuid
import dataclasses
import pandas as pd


from src.domain.valueobjects.index import Index
from src.domain.valueobjects.price_list import PriceList
from src.domain.valueobjects.news_sentiment_list import NewsSentimentList
from src.domain.valueobjects.social_sentiment_list import SocialSentimentList
from src.domain.valueobjects.date_range import DateRange
# q: why is the imports being automated as domain.valueobjects and not src.domain.valueobjects


@dataclasses.dataclass

class Equity:
    code: uuid.uuid4
    index: Index
    # pandas Series with price history and index as the timestamp
    date_range: DateRange
    price_list: PriceList
    news_sentiment_list: NewsSentimentList
    social_sentiment_list: SocialSentimentList
        
    def __init__(self, index:str, timestamps:[],price_list: [], news_sentiment_list: [], social_sentiment_list: []):
        if len(price_list) != len(news_sentiment_list) or len(price_list) != \
            len(social_sentiment_list) != len(timestamps):
            raise ValueError("The length of the equity fields are not equal.")
        
        self.code = uuid.uuid4()
        self.index = Index(index)
        self.date_range = DateRange(timestamps)
        self.price_list= PriceList(price_list)
        self.news_sentiment_list = NewsSentimentList(news_sentiment_list)
        self.social_sentiment_list = SocialSentimentList(social_sentiment_list)
        
    @classmethod
    def from_start_end_dates(cls, index:str, start_date, end_date,price_list: [], news_sentiment_list: [], social_sentiment_list: []):
        timestamps=pd.date_range(start_date, end_date).strftime("%Y-%m-%d %H:%M:%S").tolist()
        return cls(index, timestamps, price_list, news_sentiment_list, social_sentiment_list)  