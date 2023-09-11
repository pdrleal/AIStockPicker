import dataclasses

from src.domain.valueobjects.price import Price


@dataclasses.dataclass(frozen=True)
class PriceList:
    price_list: []

        