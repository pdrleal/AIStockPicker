import dataclasses


@dataclasses.dataclass(frozen=True)
class Price:
    value: float
    
        