from collections import OrderedDict
from copy import deepcopy

import beartype
import yaml

beartype.BeartypeConf.is_color = False

from beartype.typing import Any, Callable
from beartype import beartype as typeguard
from multimethod import overload
from pydantic import BaseModel
from pydantic import Field
from pydantic import field_serializer
from pathlib import PosixPath, WindowsPath


def _yaml_str_presenter(dumper, data):
    """configures yaml for dumping multiline strings
    Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
    if len(data.splitlines()) > 1:  # check for multiline string
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


yaml.add_representer(str, _yaml_str_presenter)
yaml.representer.SafeRepresenter.add_representer(str, _yaml_str_presenter)


def _yaml_pathlib_path_representer(dumper, data):
    return dumper.represent_scalar('tag:yaml.org,2002:str', str(data))
    # return dumper.represent_scalar('!Path', str(data))


yaml.add_representer(PosixPath, _yaml_pathlib_path_representer)
yaml.add_representer(WindowsPath, _yaml_pathlib_path_representer)
yaml.representer.SafeRepresenter.add_representer(PosixPath, _yaml_pathlib_path_representer)
yaml.representer.SafeRepresenter.add_representer(WindowsPath, _yaml_pathlib_path_representer)


class Object(BaseModel):
    class Config:
        arbitrary_types_allowed = True
        validate_assignment = True


def extra(obj: Object, field: str, key: str) -> Any:
    return obj.model_fields[field].json_schema_extra.get(key)


class Property(Object):
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


class Event(Object):
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
