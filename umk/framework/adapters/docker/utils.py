from umk.framework.adapters.docker.models import Image
from umk.framework.adapters.docker.models import Container


def entries(*inputs: str | Image | Container) -> list[str]:
    result = []
    for entry in inputs:
        if not issubclass(type(entry), str):
            result.append(entry.id)
        else:
            value = entry.strip()
            if value:
                result.append(value)
    return result
