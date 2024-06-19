from io import StringIO
from typing import TYPE_CHECKING, ClassVar, Self
from pydantic import BaseModel, model_validator
import re
from .helper import qstring

# RegExp to match *( ";" parameter ) in RFC 7231 sec 3.1.1.1
PARAM_REGEXP = re.compile(
    r"""; *([!#$%&'*+.^_`|~0-9A-Za-z-]+) *= *("(?:[\u000b\u0020\u0021\u0023-\u005b\u005d-\u007e\u0080-\u00ff]|\\[\u000b\u0020-\u00ff])*"|[!#$%&'*+.^_`|~0-9A-Za-z-]+) *"""
)
TEXT_REGEXP = re.compile(r"""^[\u000b\u0020-\u007e\u0080-\u00ff]+$""")
TOKEN_REGEXP = re.compile(r"""^[!#$%&'*+.^_`|~0-9A-Za-z-]+$""")

# RegExp to match quoted-pair in RFC 7230 sec 3.2.6
QESC_REGEXP = re.compile(r"""\\([\u000b\u0020-\u00ff])""")
# RegExp to match type in RFC 7231 sec 3.1.1.1
TYPE_REGEXP = re.compile(
    r"""^[!#$%&'*+.^_`|~0-9A-Za-z-]+/[!#$%&'*+.^_`|~0-9A-Za-z-]+$"""
)

MULTIPART_TYPE = "multipart/byteranges"


class ContentType(BaseModel, extra="allow"):
    HEADER_NAME: ClassVar[str] = "Content-Type"
    type: str
    if TYPE_CHECKING:

        def __init__(self, type: str, **kwargs): ...

    @model_validator(mode="after")
    def check_extra(self) -> Self:
        if self.model_extra:
            for k, v in self.model_extra.items():
                if not isinstance(v, str):
                    raise ValueError(
                        f"Only str extra param is supported. Value of {k} is not str"
                    )
        return self

    @classmethod
    def multipart(cls, boundary: str) -> Self:
        return cls(type=MULTIPART_TYPE, boundary=boundary)

    @classmethod
    def parse(cls, text: str) -> Self:
        index = text.find(";")
        type = text[:index].strip() if index != -1 else text.strip()
        if TYPE_REGEXP.search(type) is None:
            raise ValueError("invalid media type")
        params = {}
        type = type.lower()
        if index != -1:
            while m := PARAM_REGEXP.search(text, index):
                if m.start() != index:
                    raise ValueError("invalid parameter format")
                index += len(m.group(0))
                key = m.group(1).lower()
                value = m.group(2)
                if ord(value[0]) == 0x22:  # "
                    value = value[1:-1]
                    if value.find("\\") != -1:
                        value = QESC_REGEXP.sub(lambda x: x.group(1), value)
                params[key] = value

            if index != len(text):
                raise ValueError("invalid parameter format")
        return cls(type=type, **params)

    @property
    def parameters(self):
        ret = {}
        if self.__pydantic_extra__ is not None:
            ret.update(self.__pydantic_extra__)
        return ret

    def __str__(self) -> str:
        io = StringIO()
        io.write(self.type)
        for k, v in sorted(self.parameters.items()):
            io.write("; ")
            io.write(k)
            io.write("=")
            if not TOKEN_REGEXP.search(v):
                v = qstring(v)
            io.write(v)
        return io.getvalue()
