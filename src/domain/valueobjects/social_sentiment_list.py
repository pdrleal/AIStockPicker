import dataclasses

from src.domain.valueobjects.social_sentiment import SocialSentiment


@dataclasses.dataclass(frozen=True)
class SocialSentimentList:
    social_sentiment_list: []
        