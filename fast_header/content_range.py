from pydantic import BaseModel
from typing import ClassVar, List, Self, cast
import re

PAT = re.compile(r"bytes=([^;]+)")
SPLIT = re.compile(r",\s*")

RANGE_PAT = re.compile(r"""^(\w+) ((\d+)-(\d+)|\*)\/(\d+|\*)$""")


class Range(BaseModel):
    start: int = 0
    stop: int

    def __str__(self) -> str:
        return f"{self.start}-{self.stop}"

    def __len__(self) -> int:
        return self.stop - self.start

    @classmethod
    def parse(cls, http_range: str | None, size: int) -> List["Range"] | None:
        if not http_range:
            return None
        m = PAT.match(http_range)
        if m is None:
            return None
        matched = m.group(1)
        ret: List[Range] = []
        for range_spec in SPLIT.split(matched):
            if "-" not in range_spec:
                return None
            r = range_spec.split("-")
            r0 = r[0]
            r1 = r[1]
            if not r0:
                if not r1:
                    return None
                r0 = size - int(r1)
                if r0 < 0:
                    r0 = 0
                r1 = size - 1
            else:
                r0 = int(r0)
                if not r1:
                    r1 = size - 1
                else:
                    r1 = int(r1)
                    if r1 < r0:
                        return None
                    if r1 >= size:
                        r1 = size - 1
            if r0 <= r1:
                ret.append(Range(start=r0, stop=r1 + 1))
        if sum([len(r) for r in ret]) > size:
            return []
        return ret


class ContentRange(BaseModel):
    HEADER_NAME: ClassVar[str] = "Content-Range"
    unit: str = "bytes"
    range: Range | None = None
    size: int | None = None

    @classmethod
    def parse(cls, text: str) -> Self:
        m = RANGE_PAT.match(text)
        if not m:
            raise ValueError("invalid range")
        unit = m.group(1)
        start = m.group(3)
        end = m.group(4)
        size = m.group(5)
        if start and end:
            r = Range.model_validate(dict(start=start, stop=end))
        else:
            r = None
        return cls(unit=unit, range=r, size=None if size == "*" else int(size))

    def __str__(self) -> str:
        return (
            f"{self.unit} {self.range or '*'}/{'*' if self.size is None else self.size}"
        )
