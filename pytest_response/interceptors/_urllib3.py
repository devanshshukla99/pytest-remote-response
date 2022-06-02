import sys

from urllib3.connection import HTTPConnection, HTTPSConnection
from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool

from pytest_response.interceptors._urllib import (  # isort:skip
    ResponseHTTPConnection,
    ResponseHTTPSConnection,
)

__all__ = ["Response_HTTPU3_Intercepter", "Response_HTTPSU3_Intercepter", "install", "uninstall"]


class Response_HTTPU3_Intercepter(ResponseHTTPConnection, HTTPConnection):
    def __init__(self, *args, **kwargs):
        if "strict" in kwargs and sys.version_info > (3, 0):
            kwargs.pop("strict")
        kwargs.pop("socket_options", None)
        ResponseHTTPConnection.__init__(self, *args, **kwargs)
        HTTPConnection.__init__(self, *args, **kwargs)


class Response_HTTPSU3_Intercepter(ResponseHTTPSConnection, HTTPSConnection):
    is_verified = True

    def __init__(self, *args, **kwargs):
        if "strict" in kwargs and sys.version_info > (3, 0):
            kwargs.pop("strict")
        kwargs.pop("socket_options", None)
        kwargs.pop("key_password", None)
        ResponseHTTPSConnection.__init__(self, *args, **kwargs)
        HTTPSConnection.__init__(self, *args, **kwargs)


def install():
    HTTPConnectionPool.ConnectionCls = Response_HTTPU3_Intercepter
    HTTPSConnectionPool.ConnectionCls = Response_HTTPSU3_Intercepter


def uninstall():
    HTTPConnectionPool.ConnectionCls = HTTPConnection
    HTTPSConnectionPool.ConnectionCls = HTTPSConnection
