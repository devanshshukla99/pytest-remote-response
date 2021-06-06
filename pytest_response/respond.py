from pytest_response import db
import tempfile
import pytest


__all__ = [
    "urlopen_response",
    "requests_response",
    "socket_connect_response",
    "response_patch",
]


class MockHTTPResponse():
    def __init__(self, data):
        self.code = 200
        self.status = 200
        self.msg = "OK"
        self.reason = "OK"
        self.data = data.encode("utf-8")
        tmpfile = tempfile.NamedTemporaryFile()
        with open(tmpfile.name, "wb") as fp:
            fp.write(self.data)
            fp.flush()
        self.fp = open(tmpfile.name, "rb")

    def info(self):
        return {}

    def read(self, *args, **kwargs):
        return self.fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return self.fp.readline(*args, **kwargs)

    def readinto(self, n):
        return self.data[0:n]

    pass


def urlopen_response(self, http_class, req, **http_conn_args):
    """
    Mock function for urllib.request.urlopen.
    """
    data = db.get(
            url=req.get_full_url(),
            req=str(req.header_items()))
    if not data:
        pytest.xfail("No cache found")
    return MockHTTPResponse(data)


def requests_response(self, method, url, *args, **kwargs):
    """
    Mock function for urllib3 module.
    """
    full_url = f"{self.scheme}://{self.host}{url}"
    data = db.get(url=full_url)
    if not data:
        pytest.xfail("No cache found")
    return MockHTTPResponse(data)


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
    mpatch.setattr(
        "urllib.request.AbstractHTTPHandler.do_open", urlopen_response)
    mpatch.setattr(
        "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_response)
    # mpatch.setattr(
    # "socket.socket.connect", socket_connect_response)

