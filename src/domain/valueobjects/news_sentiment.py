import dataclasses


@dataclasses.dataclass(frozen=True)
class NewsSentiment:
    value: float

        