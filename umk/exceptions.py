class InternalError(Exception):
    """
    Generic internal error.
    """

    def __init__(self, message: str):
        super().__init__(message)


class GoBinaryExistsError(Exception):
    """
    Golang binary ('go' tool) does not exist.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DelveBinaryNotExistsError(Exception):
    """
    Delve binary ('dlv' tool) does not exist.
    """

    def __init__(self, message: str):
        super().__init__(message)


class RemoteExistsError(Exception):
    """
    Remote is already exists.
    """

    def __init__(self, message: str):
        super().__init__(message)


class DefaultRemoteExistsError(Exception):
    """
    Default remote is already exists.
    """

    def __init__(self, message: str):
        super().__init__(message)
