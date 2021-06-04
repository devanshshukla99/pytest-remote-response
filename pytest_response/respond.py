import json

import pytest
import pathlib
from tinydb import TinyDB, where

__all__ = [
    "urlopen_response",
    "requests_response",
    "socket_connect_response",
    "response_patch",
]

db = TinyDB("./db.json")

def urlopen_response(self, http_class, req, **http_conn_args):
    """
    Mock function for urllib.request.urlopen.
    """
    global db
    element = db.search(where("url") == req.get_full_url())[0]
    print(element)
    fname = pathlib.Path(element.get("fname"))
    if fname.exists():
        with open(fname, "rb") as fd:
            return fd.read()
    return None



def requests_response(self, method, url, *args, **kwargs):
    """
    Mock function for urllib3 module.
    """
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
    mpatch.setattr("urllib.request.AbstractHTTPHandler.do_open", urlopen_response)
    # mpatch.setattr(
    #     "urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_response
    # )
    # mpatch.setattr("socket.socket.connect", socket_connect_response)

