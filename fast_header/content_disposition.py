from io import StringIO
import os
import re
from typing import TYPE_CHECKING, ClassVar, Dict, Literal, Self, cast
from pydantic import BaseModel, Field, field_validator, model_validator
from urllib.parse import quote, unquote
from .helper import qstring

Disposition = Literal["attachment", "inline", "form-data"]

# RegExp to match percent encoding escape
HEX_ESCAPE_REGEXP = re.compile(r"""%[0-9A-Fa-f]{2}""")

# RegExp to match non-latin1 characters.
NON_LATIN1_REGEXP = re.compile(r"""[^\x20-\x7e\xa0-\xff]""")  # g
# RegExp to match quoted-pair in RFC 2616
QESC_REGEXP = re.compile(r"""\\([\u0000-\u007f])""")  # g

# RegExp for various RFC 2616 grammar
PARAM_REGEXP = re.compile(
    r""";[\x09\x20]*([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*=[\x09\x20]*("(?:[\x20!\x23-\x5b\x5d-\x7e\x80-\xff]|\\[\x20-\x7e])*"|[!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*"""
)  # g
TEXT_REGEXP = re.compile(r"""^[\x20-\x7e\x80-\xff]+$""")
TOKEN_REGEXP = re.compile(r"""^[!#$%&'*+.0-9A-Z^_`a-z|~-]+$""")

# RegExp for various RFC 5987 grammar
EXT_VALUE_REGEXP = re.compile(
    r"""^([A-Za-z0-9!#$%&+\-^_`{}~]+)'(?:[A-Za-z]{2,3}(?:-[A-Za-z]{3}){0,3}|[A-Za-z]{4,8}|)'((?:%[0-9A-Fa-f]{2}|[A-Za-z0-9!#$&+.^_`|~-])+)$"""
)
# RegExp for various RFC 6266 grammar
DISPOSITION_TYPE_REGEXP = re.compile(
    r"""^([!#$%&'*+.0-9A-Z^_`a-z|~-]+)[\x09\x20]*(?:$|;)"""
)


def _ustring(text: str) -> str:
    return "UTF-8''" + quote(text, encoding="utf-8")


def _get_latin1(name: str) -> str:
    return NON_LATIN1_REGEXP.sub("?", name)


def _decode_field(text: str) -> str:
    m = EXT_VALUE_REGEXP.search(text)
    if not m:
        raise ValueError("invalid extended field value")
    charset = m.group(1).lower()
    encoded = m.group(2)
    if charset == "iso-8859-1" or charset == "utf-8":
        return unquote(encoded, encoding=charset).replace("\x82", "?")
    else:
        raise ValueError("unsupported charset in extended field")


class ContentDisposition(BaseModel, extra="allow"):
    HEADER_NAME: ClassVar[str] = "Content-Disposition"
    type: Disposition = Field(default="attachment")
    filename: str | None = Field(default=None)
    fallback: bool | str = True

    if TYPE_CHECKING:

        def __init__(
            self,
            type: Disposition = "attachment",
            filename: str | None = None,
            fallback: bool | str = True,
            **kwargs,
        ): ...

    @field_validator("fallback")
    @classmethod
    def check_fallback(cls, v: str | bool) -> str | bool:
        if isinstance(v, str) and NON_LATIN1_REGEXP.search(v):
            raise ValueError("fallback must be ISO-8859-1 string")
        return v

    @field_validator("filename")
    @classmethod
    def check_filename(cls, v: str) -> str:
        return os.path.basename(v)

    @model_validator(mode="after")
    def check_extra(self) -> Self:
        if self.model_extra:
            for k, v in self.model_extra.items():
                if not isinstance(v, str):
                    raise ValueError(
                        f"Only str extra param is supported. Value of {k} is not str"
                    )
        return self

    @property
    def parameters(self) -> Dict[str, str]:
        ret = {}
        if self.model_extra is not None:
            ret.update(self.model_extra)
        if self.filename is None:
            return ret
        ret["filename"] = self.filename
        return ret

    @property
    def parameters_star(self) -> Dict[str, str]:
        ret = {}
        if self.model_extra is not None:
            ret.update(self.model_extra)
        if self.filename is None:
            return ret
        is_quoted = TEXT_REGEXP.search(self.filename) is not None
        fallback_name: str | None = None
        if isinstance(self.fallback, bool):
            if self.fallback:
                fallback_name = _get_latin1(self.filename)
        else:
            fallback_name = os.path.basename(self.fallback)

        if fallback_name == self.filename:
            fallback_name = None
        if (
            fallback_name is not None
            or not is_quoted
            or HEX_ESCAPE_REGEXP.search(self.filename) is not None
        ):
            ret["filename*"] = self.filename
        if is_quoted or fallback_name is not None:
            ret["filename"] = (
                fallback_name if fallback_name is not None else self.filename
            )
        return ret

    def __str__(self) -> str:
        io = StringIO()
        io.write(self.type)
        for k, v in sorted(self.parameters_star.items()):
            val = _ustring(v) if k.endswith("*") else qstring(v)
            io.write("; ")
            io.write(k)
            io.write("=")
            io.write(val)
        return io.getvalue()

    @classmethod
    def parse(cls, text: str) -> Self:
        m = DISPOSITION_TYPE_REGEXP.search(text)
        if not m:
            raise ValueError("invalid type format")
        index = len(m.group(0))
        type = cast(Disposition, m.group(1).lower())
        names = []
        params = {}
        if m.group(0).endswith(";"):
            index -= 1
        while m := PARAM_REGEXP.search(text, index):
            if m.start() != index:
                raise ValueError("invalid parameter format")
            index += len(m.group(0))
            key = m.group(1).lower()
            value = m.group(2)
            if key in names:
                raise ValueError("invalid duplicate parameter")
            names.append(key)

            if key.find("*") + 1 == len(key):
                key = key[:-1]
                value = _decode_field(value)
                params[key] = value
                continue
            if isinstance(params.get(key), str):
                continue
            if value[0] == '"':
                value = QESC_REGEXP.sub(lambda m: m.group(1), value[1:-1])
            params[key] = value
        if index != -1 and index != len(text):
            raise ValueError("invalid parameter format")
        params["type"] = type
        return cls.model_validate(params)
