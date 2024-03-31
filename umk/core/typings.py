import beartype
import pydantic as pd
from beartype.typing import *
from beartype import beartype as typeguard
from multimethod import overload as base_overload
from pydantic import Field


beartype.BeartypeConf.is_color = False

Adapter = pd.TypeAdapter
SerializationInfo = pd.SerializationInfo
overload = base_overload


class model:
    serializer = pd.model_serializer

    @staticmethod
    @typeguard
    def dict(obj: pd.BaseModel, auxiliary=None) -> dict[str, Any]:
        if obj is None:
            return auxiliary
        return obj.model_dump()

class field:
    serializer = pd.field_serializer
    validator = pd.field_validator

    @staticmethod
    def empty(value: Any) -> bool:
        t = type(value)
        if issubclass(t, bool):
            return False
        return not bool(value)


class Model(pd.BaseModel):
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True

    @model.serializer(mode="wrap")
    def serialize_model(self, wrap: Callable[[...], dict[str, Any]], info: pd.SerializationInfo) -> Any:
        result = wrap(self)
        for n, f in self.model_fields.items():
            if f.exclude:
                result.pop(n, None)
            v = getattr(self, n)
            e = self.model_config.get("excluder") or (f.json_schema_extra or {}).get("excluder")
            if e and e(v):
                result.pop(n, None)
        return result
