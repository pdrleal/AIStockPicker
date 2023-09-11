import uuid

import pandas as pd
from src.domain.valueobjects.index import Index
from src.domain.valueobjects.price_list import PriceList
from src.domain.valueobjects.news_sentiment_list import NewsSentimentList
from src.domain.valueobjects.social_sentiment_list import SocialSentimentList
from src.domain.valueobjects.date_range import DateRange
from src.domain.aggregates.equity import Equity
from src.domain.services.equity_domain_service import EquityDomainService

equity = Equity(
        index="AAPL",
        start_date="2021-01-01",
        end_date="2021-01-02",
        price_list=[1, 2],
        news_sentiment_list=[1, 2],
        social_sentiment_list=[1, 2],
    )

def test_equity_init():
    assert equity.index == Index("AAPL")
    assert equity.date_range == DateRange(["2021-01-01 00:00:00", "2021-01-02 00:00:00"])
    assert equity.price_list == PriceList([1, 2])
    assert equity.news_sentiment_list == NewsSentimentList([1, 2])
    assert equity.social_sentiment_list == SocialSentimentList([1, 2])
    
def test_equity_toDataframe():
    dates= pd.DatetimeIndex(equity.date_range.timestamps)
    indexSeries = pd.Series(equity.index.index, index=dates)
    pricesSeries= pd.Series(equity.price_list.price_list, index=dates)
    newsSentimentSeries= pd.Series(equity.news_sentiment_list.news_sentiment_list, index=dates)
    socialSentimentSeries= pd.Series(equity.social_sentiment_list.social_sentiment_list, index=dates)
    #dataframe with all series
    dataframe= pd.DataFrame({'index': indexSeries, 'price': pricesSeries, 'news_sentiment': newsSentimentSeries, 'social_sentiment': socialSentimentSeries})
    print("\n",dataframe)
    assert EquityDomainService.map_equity_to_df(equity).to_dict() == dataframe.to_dict()


"""
def test_room_model_from_dict():
    code = uuid.uuid4()
    init_dict = {
        "code": code,
        "size": 200,
        "price": 10,
        "longitude": -0.09998975,
        "latitude": 51.75436293,
    }

    room = Room.from_dict(init_dict)

    assert room.code == code
    assert room.size == 200
    assert room.price == 10
    assert room.longitude == -0.09998975
    assert room.latitude == 51.75436293


def test_room_model_to_dict():
    init_dict = {
        "code": uuid.uuid4(),
        "size": 200,
        "price": 10,
        "longitude": -0.09998975,
        "latitude": 51.75436293,
    }

    room = Room.from_dict(init_dict)
    assert room.to_dict() == init_dict


def test_room_model_comparison():
    init_dict = {
        "code": uuid.uuid4(),
        "size": 200,
        "price": 10,
        "longitude": -0.09998975,
        "latitude": 51.75436293,
    }

    room1 = Room.from_dict(init_dict)
    room2 = Room.from_dict(init_dict)

    assert room1 == room2
     """