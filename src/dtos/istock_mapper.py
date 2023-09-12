from abc import ABC
from src.domain.aggregates.stock import Stock
from src.dtos.stock_dto import StockDTO


class IStockMapper(ABC):
    def map_stock_to_dto(self, stock)->StockDTO:
        raise NotImplementedError
    def map_dto_to_stock(self, stockdto)->Stock:
        raise NotImplementedError