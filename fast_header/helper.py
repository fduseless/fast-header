from collections.abc import Callable
from typing import Any, List, cast

from pydantic import BaseModel, ValidationError, WrapValidator
from pydantic.fields import FieldInfo


def invalid_to_none(v: Any, handler: Callable[[Any], Any]) -> Any:
    try:
        return handler(v)
    except ValidationError:
        return None


Invalid2None = WrapValidator(invalid_to_none)


class HeaderModel(BaseModel):

    @classmethod
    def __field_alias__(cls, info: FieldInfo) -> List[str] | str | None:
        if not info.json_schema_extra:
            return None
        if isinstance(info.json_schema_extra, Callable):
            extra = {}
            info.json_schema_extra(extra)
        else:
            extra = info.json_schema_extra
        alias = cast(List[str] | str | None, extra.get("alias"))
        return alias

    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        ret = {}
        for k, info in cls.model_fields.items():
            alias = cls.__field_alias__(info)
            if not alias:
                continue
            if isinstance(alias, List):
                for a in alias:
                    ret[a] = k
            elif isinstance(alias, str):
                ret[alias] = k
            else:
                raise ValueError("alias should be str or List[str]")
        cls.__alias_mapping__ = ret
