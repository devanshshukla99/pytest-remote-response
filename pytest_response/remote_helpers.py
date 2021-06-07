import _socket
import pytest

from pytest_response.capture import capture_data
from pytest_response.respond import MockHTTPResponse

__all__ = [
    "urlopen_mock",
    "requests_mock",
    "socket_connect_mock",
    "remote_patch",
    "intercepted_urls",
]


_urls = {"urls_urllib": [], "urls_requests": [], "urls_socket": []}


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


def urlopen_mock(self, http_class, req, **http_conn_args):
    """
    Mock function for urllib.request.urlopen.
    """
    global _urls, _true_urlopen
    _urls.get("urls_urllib").append({"url": req.get_full_url(), "req": req})
    return MockHTTPResponse(b"", {})
    # pytest.xfail(f"The test was about to call {req.get_full_url()}")


def requests_mock(self, method, url, *args, **kwargs):
    """
    Mock function for urllib3 module.
    """
    global _urls
    full_url = f"{self.scheme}://{self.host}{url}"
    _urls.get("urls_requests").append(
        {"url": full_url, "method": method, "args": args, "kwargs": kwargs}
    )
    return MockHTTPResponse(b"", {})
    # pytest.xfail(f"The test was about to {method} {full_url}")


def socket_connect_mock(self, addr):
    """
    Mock function for socket.socket.
    """
    global _urls
    self.close()
    host = addr[0]
    port = addr[1]
    _urls.get("urls_socket").append(addr)
    pytest.xfail(f"The test was about to connect to {host}:{port}")


def urlopen(url, **kwargs):
    """Wrapper for `~urllib.request.urlopen`"""
    global _true_urlopen
    with open("debug.md", "w") as fd:
        fd.write(str(url))
    # return _true_urlopen(url, **kwargs)
    return None


def remote_patch(mpatch):
    """
    Monkey Patches urllib, urllib3 and socket.
    """
    mpatch.setattr("urllib.request.AbstractHTTPHandler.do_open", urlopen_mock)
    mpatch.setattr("urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_mock)
    # mpatch.setattr(
    #     "socket.socket.connect", socket_connect_mock)

    print("Mocked!")


@pytest.fixture
def intercepted_urls():
    """
    Pytest fixture to get the list of intercepted urls in a test
    """
    global _urls
    return _urls


def remote_dump(config):
    """
    Dumps intercepted requests to ini option ``intercept_dump_file``.
    """
    global _urls
    capture_data(_urls)
    # with open(config.getini("intercept_dump_file"), "w") as fd:
    #     json.dump(_urls, fd)
