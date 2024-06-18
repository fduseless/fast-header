from io import StringIO
import re
from typing import Annotated, ClassVar, List, Self
from pydantic import Field

from .helper import HeaderModel, Invalid2None

HEADER_REGEXP = re.compile(r'([a-zA-Z][a-zA-Z_-]*)\s*(?:=(?:"([^"]*)"|([^ \t",;]*)))?')


class CacheControl(HeaderModel):
    HEADER_NAME: ClassVar[str] = "Cache-Control"
    max_age: Annotated[int | None, Invalid2None] = Field(
        default=None, json_schema_extra=dict(alias="max-age")
    )
    max_stale: Annotated[int | bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="max-stale")
    )
    min_fresh: Annotated[int | None, Invalid2None] = Field(
        default=None, json_schema_extra=dict(alias="min-fresh")
    )
    s_maxage: Annotated[int | None, Invalid2None] = Field(
        default=None, json_schema_extra=dict(alias="s-maxage")
    )
    no_cache: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="no-cache")
    )
    no_store: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="no-store")
    )
    no_transform: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="no-transform")
    )
    only_if_cached: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="only-if-cached")
    )
    must_revalidate: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="must-revalidate")
    )
    proxy_revalidate: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="proxy-revalidate")
    )
    must_understand: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="must-understand")
    )
    private: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="private")
    )
    public: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="public")
    )
    immutable: Annotated[bool, Invalid2None] = Field(
        default=False, json_schema_extra=dict(alias="immutable")
    )
    stale_while_revalidate: Annotated[int | None, Invalid2None] = Field(
        default=None, json_schema_extra=dict(alias="stale-while-revalidate")
    )
    stale_if_error: Annotated[int | None, Invalid2None] = Field(
        default=None, json_schema_extra=dict(alias="stale-if-error")
    )

    @classmethod
    def parse(cls, text: str | None) -> Self:
        if not text:
            return cls()
        return cls.model_validate(
            {
                cls.__alias_mapping__.get(m.group(1), m.group(1)): cls.parse_value(
                    m.group(0)
                )
                for m in HEADER_REGEXP.finditer(text)
            }
        )

    @classmethod
    def parse_value(cls, text: str) -> str | bool:
        tokens = text.split("=", 1)
        if len(tokens) == 1:
            return True
        return tokens[1]

    def __str__(self) -> str:
        io = StringIO()
        for name, info in self.model_fields.items():
            v = getattr(self, name)
            alias = self.__field_alias__(info)
            if isinstance(alias, List):
                name = alias[0]
            elif isinstance(alias, str):
                name = alias
            if v is None:
                continue
            if v is False:
                continue
            if v is True:
                io.write(name)
                io.write(", ")
            else:
                io.write(name)
                io.write("=")
                io.write(str(v))
                io.write(", ")
        return io.getvalue().removesuffix(", ")
