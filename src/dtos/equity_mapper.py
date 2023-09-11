from src.domain.aggregates.equity import Equity
from src.domain.aggregates.equity import Equity
from src.dtos.iequity_mapper import IEquityMapper
from src.dtos.equity_dto import EquityDTO


class EquityMapper(IEquityMapper):
        
    def map_equity_to_dto(self, equity:Equity):
        return EquityDTO(equity.index.index, equity.date_range.timestamps, equity.price_list.price_list, equity.news_sentiment_list.news_sentiment_list, equity.social_sentiment_list.social_sentiment_list)
    
    def map_dto_to_equity(self, equitydto:EquityDTO):
        return Equity(equitydto.index, equitydto.date_range, equitydto.price_list, equitydto.news_sentiment_list, equitydto.social_sentiment_list)