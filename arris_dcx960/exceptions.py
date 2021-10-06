"""Python client for Arrix DCX960."""


class ArrisDCX960ConnectionError(Exception):
    """Exception when no connection could be made."""

    pass


class ArrisDCX960AuthenticationError(Exception):
    """Exception when authentication fails."""

    pass
