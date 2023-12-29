from umk import core


class Section:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    @core.typeguard
    def name(self, value: str):
        self._name = value

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    @core.typeguard
    def description(self, value: str):
        self._description = value

    @core.typeguard
    def __init__(self, name: str, description: str = ''):
        self._name = name
        self._description = description

    def __hash__(self):
        return hash((self._name, self._description))
