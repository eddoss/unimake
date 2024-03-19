import json as jsonlib
import pathlib
from collections import OrderedDict
from copy import deepcopy
from umk.typing import Any, Callable

import beartype
import pydantic as pd
import yaml as yamllib
from beartype import beartype as typeguard
from multimethod import overload as base_overload
from pydantic import Field
# from pydantic import validate_call

beartype.BeartypeConf.is_color = False

TypeValidationError = pd.ValidationError
SerializationInfo = pd.SerializationInfo
overload = base_overload
# typeguard = validate_call


# def typeguard(func):
#     @validate_call(config=dict(arbitrary_types_allowed=True))
#     def inner(*args, **kwargs):
#         func(*args, **kwargs)
#     return inner


# ////////////////////////////////////////////////////////////////////////////////////
# Errors
# ////////////////////////////////////////////////////////////////////////////////////

class Error(Exception):
    @property
    def messages(self) -> list:
        return self._msg

    @messages.setter
    @typeguard
    def messages(self, value: list):
        self._msg = value

    @typeguard
    def __init__(self, *messages: Any):
        super().__init__()
        self._msg = list(messages)

    def __str__(self):
        return str(self.messages)

    def __len__(self):
        len(self.messages)

    @typeguard
    def __getitem__(self, index: int) -> Any:
        return self.messages[index]

    def __iter__(self):
        for message in self.messages:
            yield message

    @typeguard
    def print(self, printer: Callable[[...], Any]):
        for message in self.messages:
            printer(message)


# ////////////////////////////////////////////////////////////////////////////////////
# Model
# ////////////////////////////////////////////////////////////////////////////////////

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
            excluder = self.model_config.get("field_excluder")
            if not excluder:
                excluder = (f.json_schema_extra or {}).get("excluder")
            if excluder and excluder(value):
                continue
            result[name] = value
        return result


# ////////////////////////////////////////////////////////////////////////////////////
# YAML
# ////////////////////////////////////////////////////////////////////////////////////

class yaml:
    @staticmethod
    def representer(*types):
        def inner(func):
            def wrapped(dumper, data):
                return func

            for t in types:
                yamllib.add_representer(t, func)
                yamllib.representer.SafeRepresenter.add_representer(t, func)
            return wrapped

        return inner

    @staticmethod
    def text(data: Model | dict[str, Any]) -> str:
        if issubclass(type(data), Model):
            d = data.model_dump()
            return yamllib.safe_dump(d)
        return yamllib.safe_dump(data)


@yaml.representer(str)
def _yaml_multiline_string(dumper, data):
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


@yaml.representer(pathlib.PosixPath, pathlib.WindowsPath)
def _yaml_pathlib(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))


# ////////////////////////////////////////////////////////////////////////////////////
# JSON
# ////////////////////////////////////////////////////////////////////////////////////

_json_representers = {}


class _JsonEncoder(jsonlib.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def default(self, value: Any):
        t = type(value)
        for rt, re in _json_representers.items():
            if issubclass(t, rt):
                return re(value)
        return super().default(value)


class json:
    @staticmethod
    def representer(*types):
        def inner(func):
            def wrapped(data):
                return func
            global _json_representers
            for t in types:
                _json_representers[t] = func
            return wrapped
        return inner

    @staticmethod
    def text(data: Model | dict | list, indent=None) -> str:
        if issubclass(type(data), Model):
            d = data.model_dump()
            return jsonlib.dumps(d, indent=indent, cls=_JsonEncoder)
        return jsonlib.dumps(data, indent=indent, cls=_JsonEncoder)


@json.representer(pathlib.PosixPath, pathlib.WindowsPath)
def _json_pathlib(data):
    return str(data)


def extra(model: Model, field: str, key: str) -> Any:
    return model.model_fields[field].json_schema_extra.get(key)


class Property(Model):
    name: str = ""
    description: str = ""
    value: Any = None

    @staticmethod
    def from_field(instance: Any, field: str):
        f = instance.model_fields[field]
        return Property(
            name=field,
            description=f.description,
            value=getattr(instance, field)
        )

    def __hash__(self):
        return hash(self.name)


class Properties:
    def __init__(self):
        self._items: OrderedDict[str, Property] = OrderedDict()

    @typeguard
    def __contains__(self, prop: str | Property) -> bool:
        t = type(prop)
        if issubclass(t, str):
            return prop in self._items
        else:
            return prop.name in self._items

    def __iter__(self):
        for prop in self._items.values():
            yield prop

    @typeguard
    def __getitem__(self, name: str) -> Property:
        return self._items[name]

    @typeguard
    def get(self, name: str, value: Any = None) -> Property:
        return self._items.get(name, value)

    @typeguard
    def add(self, prop: Property):
        self._items[prop.name] = prop

    @typeguard
    def new(self, name: str, value: Any, desc: str = ""):
        self._items[name] = Property(name=name, value=value, description=desc)


EventListener = Callable[[...], ...]
EventData = Properties


class Event(Model):
    name: str = Field(description="Event name")
    data: EventData = Field(description="Event details", default_factory=EventData)


class Emitter:
    def __init__(self):
        self._events: dict[str, list[EventListener]] = {}

    @typeguard
    def on(self, event: str, listener: EventListener):
        if event not in self._events:
            self._events[event] = []
        self._events[event].append(listener)

    @typeguard
    def off(self, event: str, listener: EventListener):
        if event in self._events:
            self._events[event].remove(listener)

    @typeguard
    def dispatch(self, event: Event):
        listeners = self._events.get(event.name)
        if listeners:
            for listener in listeners:
                listener(deepcopy(event))


