from typing import Any, Self

import pydantic
from entities import Column


class Condition(pydantic.BaseModel):
    operator: str
    left: Column | Self
    right: Any

    def __str__(self):
        return f'({self.left} {self.operator} {self.right})'
