import dataclasses

from src.domain.valueobjects.news_sentiment import NewsSentiment


@dataclasses.dataclass(frozen=True)
class NewsSentimentList:
    news_sentiment_list: []

        