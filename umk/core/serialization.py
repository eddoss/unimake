import json as jsonlib
import os
import pathlib

import yaml as yamllib

from umk.core.typings import Any
from umk.core.typings import Model
from umk.core.typings import typeguard


# ////////////////////////////////////////////////////////////////////////////////////
# YAML
# ////////////////////////////////////////////////////////////////////////////////////
class YamlNoAliasDumper(yamllib.SafeDumper):
    def ignore_aliases(self, data):
        return True

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
            return yamllib.dump(d, Dumper=YamlNoAliasDumper)
        return yamllib.dump(data, Dumper=YamlNoAliasDumper)


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
    @typeguard
    def text(data: Model | dict | list, indent=None) -> str:
        if issubclass(type(data), Model):
            d = data.model_dump()
            return jsonlib.dumps(d, indent=indent, cls=_JsonEncoder)
        return jsonlib.dumps(data, indent=indent, cls=_JsonEncoder)

    @staticmethod
    @typeguard
    def parse(text: str) -> dict | list:
        return jsonlib.loads(text)

    @staticmethod
    @typeguard
    def load(file: str | pathlib.Path) -> dict | list:
        with open(file, "r") as stream:
            return jsonlib.load(stream)

    @staticmethod
    @typeguard
    def save(data: dict | list | Model, file: str | pathlib.Path, indent=None):
        t = type(data)
        if not file.parent.exists():
            os.makedirs(file.parent)
        with open(file, "w") as stream:
            if issubclass(t, (dict, list)):
                jsonlib.dump(data, stream)
            elif issubclass(t, Model):
                text = json.text(data, indent=indent)
                stream.write(text)


@json.representer(pathlib.PosixPath, pathlib.WindowsPath)
def _json_pathlib(data):
    return str(data)

