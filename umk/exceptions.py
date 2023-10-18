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


class DelveBinaryExistsError(Exception):
    """
    Delve binary ('dlv' tool) does not exist.
    """

    def __init__(self, message: str):
        super().__init__(message)
