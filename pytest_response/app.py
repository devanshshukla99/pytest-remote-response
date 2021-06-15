import pathlib
import importlib.util
from typing import List

from pytest import MonkeyPatch

from pytest_response.database import ResponseDB
from pytest_response.logger import log


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

        self.capture = capture
        self.response = response
        self.remote = remote

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
    def available(self) -> List[str]:
        return self.available_mocks

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
        log.info(f"{mock.name} registered")
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
        try:
            for lib in self._registered_mocks.values():
                lib.uninstall()
                log.debug(f"{lib.__name__} unregistered")
            self._registered_mocks = {}
        except Exception:
            raise

    def apply(self, mock) -> None:
        """
        Activates intercepter modules.
        """
        if mock_lib := self._registered_mocks.get(mock):
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


class MalformedUrl(Exception):
    """
    Exception raised when a malformed URL is encountered.
    """

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

    pass


class InterceptorNotFound(ModuleNotFoundError):
    """
    Exception raised when the requested interceptor is not available.
    """

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

    pass
