class RemoteBlockedError(RuntimeError):
    """
    Exception raised when Remote connections are blocked.
    """

    def __init__(self, reason="A test tried to connect to internet.", *args, **kwargs):
        super(RemoteBlockedError, self).__init__(reason, *args, **kwargs)


class ResponseNotFound(RuntimeError):
    """
    Exception raised when response is not locally available.
    """

    def __init__(self, reason="Response is not available; try capturing first.", *args, **kwargs):
        super(ResponseNotFound, self).__init__(reason, *args, **kwargs)


class MalformedUrl(Exception):
    """
    Exception raised when a malformed URL is encountered.
    """

    def __init__(self, reason="Malformed URL encountered", *args, **kwargs):
        super().__init__(reason, *args, **kwargs)

    pass


class InterceptorNotFound(ModuleNotFoundError):
    """
    Exception raised when the requested interceptor is not available.
    """

    def __init__(self, reason="Interceptor not available; check `Response.available`", *args, **kwargs):
        super().__init__(reason, *args, **kwargs)

    pass


class DatabaseNotFound(Exception):
    """
    Exception raised when database is not initialized properly.
    """

    def __init__(self, reason="Database not initialized; use ``Response.setup_database``", *args, **kwargs) -> None:
        super().__init__(reason, *args, **kwargs)
