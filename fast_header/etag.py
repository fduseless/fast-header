from typing import ClassVar, Self
from pydantic import BaseModel


class ETag(BaseModel):
    HEADER_NAME: ClassVar[str] = "ETag"
    weak: bool = False
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        if value.startswith("W/"):
            return cls(weak=True, value=value[2:].strip('"'))
        return cls(value=value.strip('"'))

    def __str__(self) -> str:
        if self.weak:
            return f'W/"{self.value}"'
        return self.value
