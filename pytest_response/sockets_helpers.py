import _socket
from pytest import MonkeyPatch
from pytest_response.database import db

mpatch = MonkeyPatch()


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to use urllib.request")


class CaptureFakeSocket(_socket.socket):
    def __init__(self, *args, **kwargs):
        self._transaction = {"request": [], "response": []}
        super(CaptureFakeSocket, self).__init__(*args, **kwargs)

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
        host, port = self.getsockname()
        db.insert(url=f"sock://{host}:{port}", response=str(self._transaction))

    def close(self, *args, **kwargs):
        self._dump_transaction()
        super().close(*args, **kwargs)

    def print(self):
        print(self._transaction)

    pass


class ResponseFakeSocket(_socket.socket):
    def __init__(self, *args, **kwargs):
        self._transaction = {"request": [], "response": []}
        super(ResponseFakeSocket, self).__init__(*args, **kwargs)

    def connect(self, *args, **kwargs):
        pass

    def get(self, which, data):
        self._transaction.get(which)

    def send(self, data, *args, **kwargs):
        _ = super().send(data, *args, **kwargs)
        self.insert("request", data)
        return _

    def recv(self, size, *args, **kwargs):
        data = super().recv(size)
        self.insert("response", data)
        return data

    def _load_transaction(self):
        host, port = self.getsockname()
        self._transaction, _ = db.get(url=f"sock://{host}:{port}")

    def close(self, *args, **kwargs):
        self._dump_transaction()
        super().close(*args, **kwargs)

    def print(self):
        print(self._transaction)

    pass


def capture_install():
    global mpatch
    mpatch.setattr("socket.socket", CaptureFakeSocket)


def capture_uninstall():
    global mpatch
    mpatch.undo()


cap_install = capture_install
cap_uninstall = capture_uninstall
