from dataclasses import dataclass

@dataclass(order=True)
class Timer:
    due: float
    node: int
    name: str
