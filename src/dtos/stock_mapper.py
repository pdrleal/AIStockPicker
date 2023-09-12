from src.domain.aggregates.stock import Stock
from src.domain.aggregates.stock import Stock
from src.dtos.istock_mapper import IStockMapper
from src.dtos.stock_dto import StockDTO


class StockMapper(IStockMapper):
        
    def map_stock_to_dto(self, stock:Stock):
        return StockDTO(stock.index.index, stock.date_range.timestamps, stock.price_list.price_list, stock.news_sentiment_list.news_sentiment_list, stock.social_sentiment_list.social_sentiment_list)
    
    def map_dto_to_stock(self, stockdto:StockDTO):
        return Stock(stockdto.index, stockdto.date_range, stockdto.price_list, stockdto.news_sentiment_list, stockdto.social_sentiment_list)