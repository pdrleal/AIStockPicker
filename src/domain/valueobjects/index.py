import dataclasses


@dataclasses.dataclass(frozen=True)
class Index:
    index: str

    def __post_init__(self):
        # validate if index is uppercase
        if not self.index.isupper():
            raise ValueError("Index must be uppercase.")
        