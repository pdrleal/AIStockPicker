# write stock_dto
import dataclasses

@dataclasses.dataclass
class StockDTO:
    index: str
    date_range: []
    price_list: []
    news_sentiment_list: []
    social_sentiment_list: []
