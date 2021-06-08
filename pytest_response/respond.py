import urllib
from pytest_response.database import db
from pytest_response import urllib_helpers
from pytest_response import urllib3_helpers
from pytest_response import sockets_helpers
import tempfile
import pytest
import mmap

__all__ = [
    "urlopen_response",
    "requests_response",
    "socket_connect_response",
    "response_patch",
]


class MockHTTPResponse:
    def __init__(self, data, headers):
        self.code = 200
        self.status = 200
        self.msg = "OK"
        self.reason = "OK"
        self.headers = headers
        self.data = data
        tmpfile = tempfile.NamedTemporaryFile()
        self.fp = open(tmpfile.name, "w+b")
        self.fp.write(self.data)
        self.fp.flush()
        self.fp.seek(0)
        if self.data:
            self.fp = mmap.mmap(self.fp.fileno(), length=0)

    def info(self):
        return {}

    def read(self, *args, **kwargs):
        return self.fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return self.fp.readline(*args, **kwargs)

    def readinto(self, n):
        return self.data[0:n]

    def close(self, *args, **kwargs):
        if hasattr(self, "fp"):
            self.fp.close()

    def __exit__(self):
        if hasattr(self, "fp"):
            self.fp.close()

    def __del__(self):
        if hasattr(self, "fp"):
            self.fp.close()

    pass


def urlopen_response(self, http_class, req, **http_conn_args):
    """
    Mock function for urllib.request.urlopen.
    """
    data, headers = db.get(url=req.get_full_url(), req=str(req.header_items()))
    if not data:
        pytest.xfail("No cache found")
    return MockHTTPResponse(data, headers)


def requests_response(self, method, url, *args, **kwargs):
    """
    Mock function for urllib3 module.
    """
    full_url = f"{self.scheme}://{self.host}{url}"
    data, headers = db.get(url=full_url)
    if not data:
        pytest.xfail("No cache found")
    return MockHTTPResponse(data, headers)


def socket_connect_response(self, addr):
    """
    Mock function for socket.socket.
    """
    global _urls
    self.close()
    host = addr[0]
    port = addr[1]
    _urls.get("urls_socket").append(addr)
    pytest.xfail(f"The test was about to connect to {host}:{port}")


def response_patch(mpatch):
    """
    Monkey Patches urllib, urllib3 and socket.
    """
    # mpatch.setattr("urllib.request.AbstractHTTPHandler.do_open", urlopen_response)
    # mpatch.setattr(
    #     "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_response
    # )
    # mpatch.setattr(
    # "socket.socket.connect", socket_connect_response)

    urllib_helpers.install()
    urllib3_helpers.install()
    # sockets_helpers.res_install(mpatch)


def response_unpatch(mpatch):
    mpatch.undo()
    urllib_helpers.uninstall()
    urllib3_helpers.uninstall()
