import beartype
import pydantic as pd
from beartype.typing import *
from beartype import beartype as typeguard
from multimethod import overload as base_overload
from pydantic import Field


beartype.BeartypeConf.is_color = False

TypeValidationError = pd.ValidationError
SerializationInfo = pd.SerializationInfo
overload = base_overload


class model:
    serializer = pd.model_serializer

    @staticmethod
    def dict(obj: pd.BaseModel) -> dict[str, Any]:
        if model is not None:
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

    @model.serializer
    def _serialize_model(self):
        result = {}
        for name, f in self.model_fields.items():
            value = getattr(self, name)
            excluder = self.model_config.get("excluder")
            if not excluder:
                excluder = (f.json_schema_extra or {}).get("excluder")
            if excluder and excluder(value):
                continue
            result[name] = value
        return result
