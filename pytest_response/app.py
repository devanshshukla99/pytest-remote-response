import io
import pathlib
import importlib.util
from typing import List

from pytest import MonkeyPatch

from pytest_response.database import ResponseDB
from pytest_response.exceptions import InterceptorNotFound
from pytest_response.logger import log


class BaseMockResponse:
    def __init__(self, status: int, data: bytes, headers: dict = {}) -> None:
        self.status = self.status_code = self.code = status
        self.msg = self.reason = "OK"
        self.headers = headers
        self.will_close = True
        if not isinstance(data, io.BytesIO):
            data = io.BytesIO(data)
        self.fp = data

    def getcode(self) -> int:
        return self.code

    def flush(self):
        self.fp.flush()

    def info(self) -> dict:
        return self.headers

    def read(self, *args, **kwargs) -> bytes:
        """
        Wrapper for _io.BytesIO.read
        """
        return self.fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs) -> bytes:
        """
        Wrapper for _io.BytesIO.readline
        """
        return self.fp.readline(*args, **kwargs)

    def readinto(self, *args, **kwargs) -> bytes:
        """
        Wrapper for _io.BytesIO.readinto
        """
        return self.fp.readinto(*args, **kwargs)

    def close(self) -> None:
        if hasattr(self, "fp"):
            self.fp.close()

    pass


class Response:
    """
    Controlling and configuration application for `pytest_response`
    """

    def __init__(
        self,
        path: str = "interceptors",
        capture: bool = False,
        remote: bool = False,
        response: bool = False,
        database: bool = "db.json",
        log_level: bool = "debug",
    ) -> None:

        log.setLevel(log_level.upper())
        log.info("<------------------------------------------------------------------->")
        self._basepath = pathlib.Path(__file__).parent
        self._db_path = self._basepath.joinpath(database)
        self.db = None
        self._path_to_mocks = self._basepath.joinpath(path)
        self._available_mocks = list(self._get_available_mocks())
        self._registered_mocks = {}
        self.mpatch = MonkeyPatch()

        self.config = {"url": None, "host": None, "https": None, "headers": None}

        self.configure(remote=remote, capture=capture, response=response)

    @property
    def remote(self) -> bool:
        return self._remote

    @remote.setter
    def remote(self, value: bool) -> None:
        if type(value) is not bool:
            raise TypeError(f"Encountered `{type(value)}` instead of bool.")
        log.info(f"remote:{value}")
        self._remote = value
        return

    @property
    def capture(self) -> bool:
        return self._capture

    @capture.setter
    def capture(self, value: bool) -> None:
        if type(value) is not bool:
            raise TypeError(f"Encountered `{type(value)}` instead of bool.")
        log.info(f"capture:{value}")
        self._capture = value
        return

    @property
    def response(self) -> bool:
        return self._response

    @response.setter
    def response(self, value: bool):
        if type(value) is not bool:
            raise TypeError(f"Encountered `{type(value)}` instead of bool.")
        log.info(f"response:{value}")
        self._response = value
        return

    @property
    def available(self) -> List[str]:
        return self._available_mocks

    def configure(self, remote: bool = False, capture: bool = False, response: bool = False) -> None:
        self._remote = remote
        self._capture = capture
        self._response = response
        log.info(f"Remote:{remote}, Capture:{capture}, Response:{response}")
        return

    def setup_database(self, path: str) -> None:
        self._db_path = path
        self.db = ResponseDB(self._db_path)
        return

    def _get_available_mocks(self) -> str:
        """
        Internal method to get available interceptors.
        """
        return self._path_to_mocks.rglob("*.py")

    def registered(self) -> List[pathlib.Path]:
        """
        Returns registeres modules.
        """
        return self._registered_mocks

    def register(self, mock: str) -> None:
        """
        Registers interceptor modules; applies using `pytest_response.app.applies`
        """
        mock = self._sanatize_interceptor(mock)
        # Load interceptor
        spec = importlib.util.spec_from_file_location(mock.name, str(mock))
        mock_lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mock_lib)

        # Register for future use.
        self._registered_mocks[mock.stem] = mock_lib
        log.debug(f"{mock.name} registered")
        return

    def registermany(self, mocks: List[str]) -> None:
        """
        Wrapper for `pytest_response.app.register`
        Registers interceptor modules; applies using `pytest_response.app.applies`
        """
        for mock in mocks:
            self.register(mock)
        return

    def post(self, mock: str) -> None:
        """
        Registers and applies the mock under the same hood.

        Internally uses ``Response.register`` followed by ``Response.apply``
        """
        self.register(mock)
        self.apply(mock)
        return

    def unregister(self) -> None:
        """
        Deactivates interceptor modules.
        """
        for lib in self._registered_mocks.values():
            lib.uninstall()
            log.debug(f"{lib.__name__} unregistered")
        self._registered_mocks = {}

    def apply(self, mock) -> None:
        """
        Activates intercepter modules.
        """
        mock_lib = self._registered_mocks.get(mock, None)
        if mock_lib:
            mock_lib.install()
        return

    def unapply(self, *args, **kwargs) -> None:
        return self.unapplyall(*args, **kwargs)

    def applyall(self) -> None:
        for mock_lib in self._registered_mocks.values():
            mock_lib.install()
        return

    def unapplyall(self) -> None:
        """
        Un-applies interceptor modules.
        """
        for mock_lib in self._registered_mocks.values():
            mock_lib.uninstall()
        log.debug("interceptors unapplied")

    def insert(self, url, response, headers, *args, **kwargs):
        """
        Wrapper function for `pytest_response.database.db.insert`
        """
        return self.db.insert(url, response, headers, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        """
        Wrapper function for `pytest_response.database.db.get`
        """
        return self.db.get(url, *args, **kwargs)

    def _sanatize_interceptor(self, mock: str) -> pathlib.Path:
        mock = self._path_to_mocks.joinpath(mock)
        if not mock.suffix:
            # If supplied mock-name is missing .py, add it.
            mock = mock.with_suffix(".py")
        if mock not in self._get_available_mocks():
            # If interceptor is not available raise/
            raise InterceptorNotFound(f"Requested interceptor `{mock}` is not available; check `available()`")
        return mock

    pass
