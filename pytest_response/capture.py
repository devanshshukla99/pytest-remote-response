import json
from pytest_response import remote_status

import pytest

from urllib.request import urlopen
from tinydb import TinyDB, where
import shutil
import tempfile
import datetime
import hashlib


__all__ = [
    "urlopen_response",
    "requests_response",
    "socket_connect_response",
    "response_patch",
]


def capture_url_data(remote_urls):
    db = TinyDB("./db.json")
    # urlopen
    links = remote_urls.get("urls_urllib")
    for link in links:
        with urlopen(link) as response:
            with tempfile.NamedTemporaryFile(delete=False, dir="./") as tmp_file:
                shutil.copyfileobj(response, tmp_file)
            print(tmp_file.name)
            # if db.search(where("url") == link):
            #     db.update()
            db.upsert(
                {
                    "url": link,
                    "fname": tmp_file.name,
                    "cache_date": str(datetime.datetime.now()),
                    "hash": None
                },
                where("url") == link)
            # db.insert(
            #     {
            #         "url": link,
            #         "fname": tmp_file.name,
            #         "cache_date": str(datetime.datetime.now()),
            #         "hash": None
            #     })
            print("Inserted!")





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
