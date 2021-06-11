# flake8:noqa
import _socket
import pytest

from pytest_response import sockets_helpers
from pytest_response.capture import capture_data
from pytest_response.respond import MockHTTPResponse

# import gevent
# from gevent import socket, monkey


__all__ = [
    "urlopen_mock",
    "requests_mock",
    "socket_connect_mock",
    "remote_patch",
    "intercepted_urls",
]


_urls = {"urls_urllib": [], "urls_requests": [], "urls_socket": []}

socket_req = []
socket_res = []


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
    _urls.get("urls_requests").append({"url": full_url, "method": method, "args": args, "kwargs": kwargs})
    return MockHTTPResponse(b"", {})
    # pytest.xfail(f"The test was about to {method} {full_url}")


def socket_connect_mock(self, addr):
    """
    Mock function for socket.socket.
    """
    # global _urls
    # # self.close()
    host = addr[0]
    port = addr[1]
    # _urls.get("urls_socket").append(addr)
    # return _socket.socket.connect(self, addr)
    pytest.xfail(f"The test was about to connect to {host}:{port}")


def socket_send_mock(self, data, *args, **kwargs):
    """
    Mock function for socket.socket.send.
    """
    # global _urls
    # print("\n\033[32m ************************************ \033[0m")
    # print(data)
    # print("\n\033[32m ************************************ \033[0m")
    socket_req.append(data)
    # _s = _socket.socket.sendall(self, data, *args, **kwargs)
    _s = _socket.socket.sendall(self, data, *args, **kwargs)
    # _s = self.sendall(data, *args, **kwargs)
    # if len(self.getsockname()) == 4:
    #     host, port, _, _ = self.getsockname()
    # else:
    #     host, port = self.getsockname()
    return _s
    # pytest.xfail(f"The test was about to connect to {host}:{port}")


def socket_recv_mock(self, size, *args, **kwargs):
    """
    Mock function for socket.socket.send.
    """
    # global _urls
    # print("\n\033[32m ************************************ \033[0m")
    # print(data)
    # print("\n\033[32m ************************************ \033[0m")
    # _s = gevent.socket.recv(self, size)
    _s = _socket.socket.recv(self, size)
    socket_res.append(_s)
    # _s = self.recv(size, *args, **kwargs)
    # print("\n\033[32m ************************************ \033[0m")
    # if len(self.getsockname()) == 4:
    #     host, port, _, _ = self.getsockname()
    # else:
    #     host, port = self.getsockname()
    return _s
    # pytest.xfail(f"The test was about to connect to {host}:{port}")


def remote_patch(mpatch):
    """
    Monkey Patches urllib, urllib3 and socket.
    """
    mpatch.setattr("urllib.request.AbstractHTTPHandler.do_open", urlopen_mock)
    mpatch.setattr("urllib3.connectionpool.HTTPConnectionPool.urlopen", requests_mock)
    mpatch.setattr("socket.socket.connect", socket_connect_mock)
    # sockets_helpers.cap_install(mpatch)
    # mpatch.setattr("socket.socket.connect", socket_connect_mock)
    # mpatch.setattr("socket.socket.send", socket_send_mock)
    # mpatch.setattr("socket.socket.recv", socket_recv_mock)

    print("Mocked!")


def remote_unpatch(mpatch):
    """
    Un-Monkey Patches urllib, urllib3 and socket.
    """
    mpatch.undo()
    capture_data(_urls)


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
    # capture_data(_urls)
    # with open(config.getini("intercept_dump_file"), "w") as fd:
    #     json.dump(_urls, fd)
    # print(socket_req)
    # print(socket_res)
    # print(_urls["urls_socket"])
