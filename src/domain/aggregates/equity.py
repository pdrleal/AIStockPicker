import uuid
import dataclasses

@dataclasses.dataclass

class Equity:
    code: uuid.UUID
    index: str
    price: int
    
    @classmethod
    def from_dict(cls, d):
        return cls(**d)
    
    def to_dict(self):
        return dataclasses.asdict(self)