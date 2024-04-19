import abc
from collections import OrderedDict

from umk.core.serialization import json
from umk.core.typings import Any
from umk.core.typings import Model, Field
from umk.core.typings import typeguard


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
    def __init__(self, *properties: Property):
        self._items: OrderedDict[str, Property] = OrderedDict()
        for prop in properties:
            self._items[prop.name] = prop

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
    def __setitem__(self, name: str, value: Property):
        self._items[name] = value

    def __bool__(self):
        return bool(self._items)

    @typeguard
    def get(self, name: str, value: Any = None) -> Property:
        return self._items.get(name, value)

    @typeguard
    def add(self, prop: Property):
        self._items[prop.name] = prop

    @typeguard
    def new(self, name: str, value: Any, desc: str = ""):
        self._items[name] = Property(name=name, value=value, description=desc)


class Object(Model):
    type: str = Field(
        default="",
        description="Object type name"
    )
    properties: Properties = Field(
        default_factory=Properties,
        description="Object properties"
    )


@json.representer(Properties)
def serializing(properties: Properties):
    result = []
    for prop in properties:
        result.append(prop.model_dump())
    return result


@json.representer(Object)
def serializing(obj: Object):
    return obj.model_dump()
