from typing import ClassVar, Self
from pydantic import BaseModel


class ETag(BaseModel):
    HEADER_NAME: ClassVar[str] = "ETag"
    weak: bool = False
    value: str

    @classmethod
    def parse(cls, text: str) -> Self:
        if text.startswith("W/"):
            return cls(weak=True, value=text[2:].strip('"'))
        return cls(value=text.strip('"'))

    def __str__(self) -> str:
        if self.weak:
            return f'W/"{self.value}"'
        return self.value
