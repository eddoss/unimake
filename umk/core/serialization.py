import json as jsonlib
import pathlib

import yaml as yamllib

from umk.core.typing import Any
from umk.core.typing import Model


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

