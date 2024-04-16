import copy
from umk.core.typings import Any

from umk import core
from umk.framework.utils import caller
from umk.framework.filesystem import Path


class Opt(core.Model):
    name: str = core.Field(default="", description="CLI option (or flag) qualified name")

    def list(self) -> list[str]: ...


class Str(Opt):
    value: str = core.Field(default="", description="Option value")
    surr: str = core.Field(default="", description="Surrounded symbols")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")

    def list(self) -> list[str]:
        self.surr = self.surr.strip()
        if self.equal == "":
            return [self.name, f'{self.surr}{self.value}{self.surr}']
        else:
            return [f"{self.name}{self.equal}{self.surr}{self.value}{self.surr}"]


class File(Opt):
    value: Path = core.Field(default="", description="Option value")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")

    def list(self) -> list[str]:
        if self.equal == "":
            return [self.name, f'{self.value.as_posix()}']
        else:
            return [f"{self.name}{self.equal}{self.value.as_posix()}"]


class Int(Opt):
    value: int = core.Field(default=0, description="Option value")
    surr: str = core.Field(default="", description="Surrounded symbols")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")

    def list(self) -> list[str]:
        self.surr = self.surr.strip()
        if self.equal == "":
            return [self.name, f'{self.surr}{self.value}{self.surr}']
        else:
            return [f"{self.name}{self.equal}{self.surr}{self.value}{self.surr}"]


class Bool(Opt):
    value: bool = core.Field(default=False, description="Option value")
    surr: str = core.Field(default="", description="Surrounded symbols")
    kind: str = core.Field(default="", description="Represent style (alpha, digit, word)")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")

    def list(self) -> list[str]:
        self.surr = self.surr.strip()
        quoted = lambda string: f"{self.surr}{string}{self.surr}"
        if self.kind == "digit":
            return [self.name, quoted(str(int(self.value)))]
        elif self.kind == "word":
            return [self.name, quoted({True: "yes", False: "no"}[self.value])]
        return {True: [self.name], False: []}[self.value]


class List(Opt):
    value: list = core.Field(default_factory=list, description="Option value")
    split: str = core.Field(default="")
    surr: str = core.Field(default="", description="Surrounded symbols of the whole result")
    surr_each: str = core.Field(default="", description="Surrounded symbols of the each item")
    multi: bool = core.Field(default=False, description="Use option for each item (--opt=item1 --opt=item2 ...)")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")

    def list(self) -> list[str]:
        sa = self.surr.strip()
        se = self.surr_each.strip()
        eq = self.equal if self.equal else " "
        sp = self.split if self.split else " "
        chunks = []
        for value in self.value:
            value = f'{se}{value}{se}'
            if self.multi:
                if eq.strip():
                    chunk = [f"{self.name}{eq}{value}"]
                else:
                    chunk = [self.name, value]
            else:
                chunk = [value]
            chunks += chunk
        if not self.multi:
            return [f"{self.name}{eq}{sa}{sp.join(chunks)}{sa}"]
        return chunks


class Dict(Opt):
    value: dict = core.Field(default_factory=dict, description="Option value")
    split: str = core.Field(default=" ")
    surr: str = core.Field(default="", description="Surrounded symbols of the whole result")
    surr_each: str = core.Field(default="", description="Surrounded symbols of the each item")
    multi: bool = core.Field(default=False, description="Use option for each item (--opt=item1 --opt=item2 ...)")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")
    equal_each: str = core.Field(default="=", description="Value equal symbol (--opt=k:v, --opt=k=v, ...)")
    equal_each_skip: bool = core.Field(default=True, description="Skip equal symbol when value is empty")

    def list(self) -> list[str]:
        sa = self.surr.strip()
        se = self.surr_each.strip()
        eq = self.equal if self.equal else " "
        ee = self.equal_each if self.equal_each else " "
        sp = self.split if self.split else " "
        chunks = []
        for k, v in self.value.items():
            if v:
                item = f'{se}{k}{ee}{v}{se}'
            else:
                item = f'{se}{k}{se}'
            if self.multi:
                if eq.strip():
                    chunk = [f"{self.name}{eq}{item}"]
                else:
                    chunk = [self.name, item]
            else:
                chunk = [item]
            chunks += chunk
        if not self.multi:
            return [f"{self.name}{eq}{sa}{sp.join(chunks)}{sa}"]
        return chunks


class Obj(Opt):
    value: Any = core.Field(default=None, description="Option value")
    surr: str = core.Field(default="", description="Surrounded symbols")
    equal: str = core.Field(default="", description="CLI option (flag) equal symbol (--opt=val, --opt val, ...)")

    def list(self) -> list[str]:
        self.surr = self.surr.strip()
        res = str(self.value).lower()
        if self.equal == "":
            return [self.name, f'{self.surr}{res}{self.surr}']
        else:
            return [f"{self.name}{self.equal}{self.surr}{res}{self.surr}"]


class Arg(Opt):
    value: Any = core.Field(default=None, description="Argument value")
    # required: bool = core.Field(default=False, description="Whether argument is required or not")

    def list(self) -> list[str]:
        if self.value is not None:
            return [str(self.value)]
        return []


class Args(Opt):
    value: list[Any] = core.Field(default=None, description="Argument values")

    def list(self) -> list[str]:
        result = []
        for entry in self.value:
            if entry is not None:
                result.append(str(entry))
        return result


class NoEmpty(core.Model):
    class Config(core.Model.Config):
        excluder = core.field.empty


class Options(NoEmpty):
    def serialize(self) -> list[str]:
        result = []
        for name in self.model_fields:
            f = self.model_fields[name]
            cli: None | Opt | Arg | Args = f.json_schema_extra.get("cli") if f.json_schema_extra else None
            if not cli:
                result.extend(getattr(self, name).serialize())
            elif issubclass(type(cli), Opt):
                items = self._opt(cli, name)
                result.extend(items)
            elif issubclass(type(cli), Arg):
                items = self._arg(cli, name)
                result.extend(items)
            elif issubclass(type(cli), Args):
                items = self._args(cli, name)
                result.extend(items)
            else:
                items = self._other(cli, name)
                result.extend(items)
        return result

    def _opt(self, opt: Opt, field: str) -> list[str]:
        value = getattr(self, field)
        if issubclass(type(value), (list, dict, set)) and not value or value is None:
            return []
        o = copy.deepcopy(opt)
        o.value = value
        return o.list()

    def _arg(self, arg: Arg, field: str) -> list[str]:
        value = getattr(self, field)
        if issubclass(type(value), (list, dict, set)) and not value or value is None:
            return []
        a = copy.deepcopy(arg)
        a.value = value
        return a.list()

    def _args(self, args: Args, field: str) -> list[str]:
        value = getattr(self, field)
        if issubclass(type(value), (list, dict, set)) and not value or value is None:
            return []
        a = copy.deepcopy(args)
        a.value = value
        return a.list()

    def _other(self, cli: Any, field: str) -> list[str]:
        core.globals.print(f"[bold yellow] {caller()}: invalid cli option type, name='{field}' type='{type(cli)}'")
        return []
