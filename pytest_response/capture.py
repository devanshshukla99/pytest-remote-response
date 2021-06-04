import json

import pytest

from urllib.request import urlopen


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


def urlopen_capture(capture_url):
    """
    Mock function for urllib.request.urlopen.
    """
    print(urlopen(capture_url))


# def requests_response(self, method, url, *args, **kwargs):
#     """
#     Mock function for urllib3 module.
#     """
#     global _urls
#     full_url = f"{self.scheme}://{self.host}{url}"
#     _urls.get("urls_requests").append(full_url)
#     pytest.xfail(f"The test was about to {method} {full_url}")


# def socket_connect_response(self, addr):
#     """
#     Mock function for socket.socket.
#     """
#     global _urls
#     self.close()
#     host = addr[0]
#     port = addr[1]
#     _urls.get("urls_socket").append(addr)
#     pytest.xfail(f"The test was about to connect to {host}:{port}")
