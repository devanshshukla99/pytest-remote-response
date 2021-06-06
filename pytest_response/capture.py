from pytest_response import db
import pytest

from urllib.request import urlopen
import requests

__all__ = [
    "capture_url_data",
    "capture_requests_data",
    # "socket_connect_response",
    # "response_patch",
]


def capture_data(remote_urls):
    capture_url_data(remote_urls.get("urls_urllib"))
    capture_requests_data(remote_urls.get("urls_requests"))
    return


def capture_url_data(links):
    # urlopen
    for link in links:
        url = link.get("url")
        req = link.get("req")
        with urlopen(url) as response:
            db.insert(
                url,
                {
                    "url": url,
                    "request": str(req.header_items()),
                    "response": response.read().decode("utf-8")
                })
            print("Inserted!")


def capture_requests_data(links):
    # urlopen
    for link in links:
        url = link.get("url")
        method = link.get("method")
        args = link.get("args")
        kwargs = link.get("kwargs")
        with requests.get(url) as response:
            db.insert(
                url,
                {
                    "url": url,
                    "method": method,
                    "args": str(args),
                    "kwargs": str(kwargs),
                    "response": response.content.decode("utf-8")
                })
            print("Inserted!")



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
