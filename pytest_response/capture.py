from pytest_response.database import db
from urllib.error import URLError, HTTPError
from urllib.request import urlopen
import requests

__all__ = [
    "capture_url_data",
    "capture_requests_data",
]


def capture_data(remote_urls):
    capture_url_data(remote_urls.get("urls_urllib"))
    capture_requests_data(remote_urls.get("urls_requests"))
    return


def capture_url_data(links):
    # urlopen
    for link in links:
        url = link.get("url")
        print(f"capturing: {url}")
        try:
            with urlopen(url) as response:
                db.insert(
                    url, response=response.read(), headers=str(dict(response.headers))
                )
        except (HTTPError, URLError) as e:
            print(f"capturing failed:{url} status:{e.reason}")


def capture_requests_data(links):
    # urlopen
    for link in links:
        url = link.get("url")
        method = link.get("method")
        print(f"capturing: {url}")
        try:
            with requests.get(url) as response:
                db.insert(
                    url,
                    response=response.content,
                    method=method,
                    headers=str(response.headers),
                )
        except (HTTPError, URLError):
            print(f"capturing failed:{url}")


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
