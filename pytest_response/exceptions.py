class RemoteBlockedError(RuntimeError):
    """
    Exception raised when Remote connections are blocked.
    """

    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to connect to internet.")


class ResponseNotFound(RuntimeError):
    """
    Exception raised when response is not locally available.
    """

    def __init__(self, *args, **kwargs):
        super(ResponseNotFound, self).__init__("Response is not available; try capturing first.")


class MalformedUrl(Exception):
    """
    Exception raised when a malformed URL is encountered.
    """

    def __init__(self, reason):
        super().__init__(reason)

    pass


class InterceptorNotFound(ModuleNotFoundError):
    """
    Exception raised when the requested interceptor is not available.
    """

    def __init__(self, reason):
        super().__init__(reason)

    pass
