import json

import pytest

__all__ = [
    "urlopen_response",
    "requests_response",
    "socket_connect_response",
    "response_patch",
]

_urls = {
    "urls_urllib": [],
    "urls_requests": [],
    "urls_socket": []
}


def urlopen_response(self, http_class, req, **http_conn_args):
    """
    Mock function for urllib.request.urlopen.
    """
    global _urls
    _urls.get("urls_urllib").append(req.get_full_url())


def requests_response(self, method, url, *args, **kwargs):
    """
    Mock function for urllib3 module.
    """
    global _urls
    full_url = f"{self.scheme}://{self.host}{url}"
    _urls.get("urls_requests").append(full_url)
    pytest.xfail(f"The test was about to {method} {full_url}")


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
    mpatch.setattr(
        "socket.socket.connect", socket_connect_response)


@pytest.fixture
def intercepted_urls():
    """
    Pytest fixture to get the list of intercepted urls in a test
    """
    global _urls
    return _urls
