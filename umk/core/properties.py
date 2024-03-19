from collections import OrderedDict

from umk.core.typing import Any
from umk.core.typing import Model
from umk.core.typing import typeguard


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
