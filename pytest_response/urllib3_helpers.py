import sys
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
from urllib3.connection import HTTPConnection, HTTPSConnection
from pytest_response.urllib_helpers import (
    ResponseHTTPConnection,
    ResponseHTTPSConnection,
)

socket_req = []
socket_res = []


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


class _Response_HTTPU3_Intercepter(ResponseHTTPConnection, HTTPConnection):
    def __init__(self, *args, **kwargs):
        if "strict" in kwargs and sys.version_info > (3, 0):
            kwargs.pop("strict")
        kwargs.pop("socket_options", None)
        ResponseHTTPConnection.__init__(self, *args, **kwargs)
        HTTPConnection.__init__(self, *args, **kwargs)


class _Response_HTTPSU3_Intercepter(ResponseHTTPSConnection, HTTPSConnection):
    is_verified = True

    def __init__(self, *args, **kwargs):
        if "strict" in kwargs and sys.version_info > (3, 0):
            kwargs.pop("strict")
        kwargs.pop("socket_options", None)
        kwargs.pop("key_password", None)
        ResponseHTTPSConnection.__init__(self, *args, **kwargs)
        HTTPSConnection.__init__(self, *args, **kwargs)


def install():
    HTTPConnectionPool.ConnectionCls = _Response_HTTPU3_Intercepter
    HTTPSConnectionPool.ConnectionCls = _Response_HTTPSU3_Intercepter


def uninstall():
    HTTPConnectionPool.ConnectionCls = HTTPConnection
    HTTPSConnectionPool.ConnectionCls = HTTPSConnection
