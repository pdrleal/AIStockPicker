from abc import ABC
from src.domain.aggregates.equity import Equity
from src.dtos.equity_dto import EquityDTO


class IEquityMapper(ABC):
    def map_equity_to_dto(self, equity)->EquityDTO:
        raise NotImplementedError
    def map_dto_to_equity(self, equitydto)->Equity:
        raise NotImplementedError