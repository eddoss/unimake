from umk import core
from umk.core.typings import Any, TypeVar

Value = str | int | bool | float
ValueTypes = {str, int, bool, float}


Config = core.Model


class Instance:
    def __init__(self):
        self.entries: set[str] = set()
        # self.struct = None
        self.object = None

    def set(self, entry: str, value: Value):
        if entry not in self.entries:
            # TODO Raise entry access error
            pass
        tokens = entry.replace("-", "_").split(".")
        if len(tokens) == 1:
            setattr(self.object, tokens[0], value)
        else:
            attr = tokens[-1]
            curr = self.object
            for token in tokens[:-1]:
                curr = getattr(curr, token)
            setattr(curr, attr, value)

    def get(self, entry: str, on_err: Any = None) -> None | Value:
        if entry not in self.entries:
            return on_err
        result = self.object
        tokens = entry.replace("-", "_").split(".")
        for token in tokens:
            result = getattr(result, token)
        return result

    def apply(self, *presets: dict[str, Value]):
        for preset in presets:
            for k, v in preset.items():
                self.set(k, v)

    def setup(self):
        def recursive(root: core.Model, parent: str, tokens: set[str]):
            for f in root.model_fields.keys():
                v = getattr(root, f)
                t = type(v)
                if t in (str, int, bool, float):
                    tokens.add(f"{parent}.{f}".lstrip(".").replace("_", "-"))
                elif issubclass(t, core.Model):
                    recursive(v, f"{parent}.{f}", tokens)
        recursive(self.object, "", self.entries)


Struct = TypeVar("Struct", bound=core.Model)


def register(factory):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def preset(name: str = ""):
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


def get() -> Struct:
    # See implementation in runtime.Instance.implementation()
    raise NotImplemented()


# if __name__ == '__main__':
#     class Conf(core.Model):
#         class B(core.Model):
#             q: int = core.Field(default=2, description="Some value Q")
#             w: str = core.Field(default="www", description="Some value W")
#
#             class Z(core.Model):
#                 g: int = core.Field(default=2, description="Some value g")
#
#             z: Z = core.Field(default_factory=Z, description="Some value Z")
#
#         a: int = core.Field(default=4, description="Some value A")
#         b: B = core.Field(default_factory=B, description="Some value A")
#
#         def entries(self):
#             result = []
#
#             def recursive(root: core.Model, parent: str, tokens: list[str]):
#                 for f in root.model_fields.keys():
#                     v = getattr(root, f)
#                     t = type(v)
#                     if t in (str, int, bool, float):
#                         tokens.append(f"{parent}.{f}".lstrip("."))
#                     elif issubclass(t, core.Model):
#                         recursive(v, f"{parent}.{f}", tokens)
#
#             recursive(self, "", result)
#             return result
#
#
#     c = Conf()
#     print(c.entries())
#
#     # t = c
#     # v = ["world"]
#     # p = "environ.files"
#     #
#     # a = getattr(c, "environ")
#     # setattr(a, "files", v)
#     #
#     # print(c.environ.files)
#     #
#     # o = c
#     # for name in "environ.files".split("."):
#     #     o = getattr(o, name)
#     # print(o)
