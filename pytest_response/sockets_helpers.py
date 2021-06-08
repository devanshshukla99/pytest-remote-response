import ast
import _socket
import pytest
from pytest_response.database import db


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


class CaptureFakeSocket(_socket.socket):
    def __init__(self, *args, **kwargs):
        self._transaction = {"request": [], "response": []}
        self.hostport = {"host": None, "port": None}
        super(CaptureFakeSocket, self).__init__(*args, **kwargs)

    def connect(self, addr):
        # self.addr = addr
        self.hostport["host"] = addr[0]
        self.hostport["port"] = addr[1]
        super().connect(addr)

    def insert(self, which, data):
        self._transaction.get(which).append(data)

    def send(self, data, *args, **kwargs):
        _ = super().send(data, *args, **kwargs)
        self.insert("request", data)
        return _

    def recv(self, size, *args, **kwargs):
        data = super().recv(size)
        self.insert("response", data)
        return data

    def _dump_transaction(self):
        # host = self.addr[0]
        # port = self.addr[1]
        # host = _socket.gethostbyname(host)
        # host, port = _socket.socket.getpeername(self)
        # print(self, self.hostport)
        host, port = self.hostport["host"], self.hostport["port"]
        if host:
            db.insert(
                url=f"sock://{host}:{port}",
                response=str(self._transaction).encode("utf-8"),
            )

    def close(self, *args, **kwargs):
        self._dump_transaction()
        # asyncio.run(self._dump_transaction())
        super().close(*args, **kwargs)

    def __exit__(self):
        self.close()

    # def __del__(self):
    #     self.close()

    def print(self):
        print(self._transaction)

    pass


class ResponseFakeSocket(_socket.socket):
    def __init__(self, *args, **kwargs):
        self._transaction = {"request": [], "response": []}
        super(ResponseFakeSocket, self).__init__(*args, **kwargs)

    def connect(self, addr, *args, **kwargs):
        self._load_transaction(addr)
        pass

    def get_request(self):
        if _reqs := self._transaction.get("request"):
            return _reqs.pop(0)

    def get_response(self):
        if _ress := self._transaction.get("response"):
            return _ress.pop(0)

    def send(self, data, *args, **kwargs):
        print(self.get_request())
        pass

    def recv(self, size, *args, **kwargs):
        data = self.get_response()
        return data

    def _load_transaction(self, addr):
        host, port = addr
        host = _socket.gethostbyname(host)
        self._transaction, _ = db.get(url=f"sock://{host}:{port}")
        self._transaction = ast.literal_eval(self._transaction.decode("utf-8"))

    def close(self, *args, **kwargs):
        super().close(*args, **kwargs)

    def print(self):
        print(self._transaction)

    pass


def _capture_install(mpatch):
    mpatch.setattr("socket.socket", CaptureFakeSocket)


def _response_install(mpatch):
    mpatch.setattr("socket.socket", ResponseFakeSocket)


def _uninstall(mpatch):
    mpatch.undo()


cap_install = _capture_install
res_install = _response_install
uninstall = _uninstall
