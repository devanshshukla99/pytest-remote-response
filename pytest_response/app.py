import io
import pathlib
import importlib.util
from types import ModuleType
from typing import Dict, List

from pytest import MonkeyPatch

from pytest_response.database import ResponseDB
from pytest_response.exceptions import DatabaseNotFound, InterceptorNotFound
from pytest_response.logger import log


class BaseMockResponse:
    """
    Basic response for mocking requests.

    Parameters
    ----------
    status : `int`
        Status code of the response.
    data : `bytes`
        Response data.
    headers : `dict`, optional
        Default to `{}`.
    """

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
    Controlling and configuration application for ``pytest-remote-response``

    Parameters
    ----------
    path : `str`, optional
        Path for the interceptors.
        Defaults to `pytest_response.interceptors`
    capture : `bool`, optional
        if `True` captures data and headers in the database.
        Defaults to `False`
    remote : `bool`, optional
        if `False` blocks connection requests.
        Defaults to `False`
    response : `bool`, optional
        if `True` responds with data and headers from the database.
        Defaults to `False`
    log_level : `str`, optional
        Log level.
        Defaults to `debug`

    Examples
    --------
    >>> from pytest_response import response
    >>> response.setup_database({{ Path to the database}})
    >>> response.post({{ Interceptor }})
    >>> ...
    >>> response.unpost()
    """

    def __init__(
        self,
        path: str = "interceptors",
        capture: bool = False,
        remote: bool = False,
        response: bool = False,
        log_level: str = "debug",
    ) -> None:

        log.setLevel(log_level.upper())
        log.info("<------------------------------------------------------------------->")

        self._basepath = pathlib.Path(__file__).parent

        self._path_to_mocks = self._basepath.joinpath(path)
        self._available_mocks = list(self._get_available_mocks())
        self._registered_mocks = {}
        self.mpatch = MonkeyPatch()

        self.db = None

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
        """
        Helper method to configure interceptors.

        Parameters
        ----------
        remote : `bool`, optional
            If `False` blocks connection requests.
            Defaults to `False`.
        capture : `bool`, optional
            If `True` captures data and headers in the database.
            Defaults to `False`.
        response : `bool`, optional
            If `True` responds with data and headers from the database.
            Defaults to `False`.
        """
        self._remote = remote
        self._capture = capture
        self._response = response
        log.info(f"Remote:{remote}, Capture:{capture}, Response:{response}")
        return

    def setup_database(self, path: str) -> None:
        """
        Method to setup-up database.

        Parameters
        ----------
        path : `str`
            Path for the database.
        """
        self._db_path = path
        self.db = ResponseDB(self._db_path)
        return

    def _get_available_mocks(self) -> List[str]:
        """
        Internal method to get available interceptors.
        """
        return self._path_to_mocks.rglob("*.py")

    def registered(self) -> Dict[str, ModuleType]:
        """
        Returns registered modules.

        Returns
        -------
        `list` of `pathlib.Path`
            Returns the list of registered interceptors.
        """
        return self._registered_mocks

    def register(self, mock: str) -> None:
        """
        Registers interceptor modules; applies using ``pytest_response.app.applies``

        Parameters
        ----------
        mock : `str`
            Interceptor; check ``Response.available`` for more info.
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

        Parameters
        ----------
        mocks : `list`
            List of interceptors to be registered.
        """
        for mock in mocks:
            self.register(mock)
        return

    def post(self, mock: str) -> None:
        """
        Registers and applies the mock under the same hood.

        Internally uses ``Response.register`` followed by ``Response.apply``

        Parameters
        ----------
        mock : `str`
            Registers and applies the mock.
        """
        self.register(mock)
        self.apply(mock)
        return

    def unpost(self) -> None:
        """
        Unapplied and unregisters mocks under the same hood.

        Internally uses ``Response.unapplyall()`` followed by ``Response.unregister``
        """
        self.unapplyall()
        self.unregister()

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

        Parameters
        ----------
        mock : `str`
            Applies the mock.
        """
        mock_lib = self._registered_mocks.get(mock, None)
        if mock_lib:
            mock_lib.install()
        return

    def unapply(self, *args, **kwargs) -> None:
        """
        Wrapper method for ``Response.unapplyall()``
        """
        return self.unapplyall(*args, **kwargs)

    def applyall(self) -> None:
        """
        Reiterates over registered mocks to apply them all.
        """
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

    def insert(self, url, response, headers, status, *args, **kwargs):
        """
        Wrapper function for ``pytest_response.database.db.insert``

        Parameters
        ----------
        url : `str`
            URL of the dump.
        response : `bytes`
            Data captured.
        headers : `str`
            Headers captured.
        status : `int`
            Status code of the response.
        **kwargs : `dict`
            Any additional parameter to be dumped.
        """
        if not self.db:
            log.error("`Response.insert` called without setting up the database.")
            raise DatabaseNotFound
        return self.db.insert(url, response, headers, *args, **kwargs)

    def get(self, url, *args, **kwargs):
        """
        Wrapper function for ``pytest_response.database.db.get``

        Parameters
        ----------
        url : `str`
            URL to be queried.

        Returns
        -------
        status : `int`
            Status code
        data : `bytes`
            Response data.
        headers : `dict`
            Response header.
        """
        if not self.db:
            log.error("`Response.get` called without setting up the database.")
            raise DatabaseNotFound
        return self.db.get(url, *args, **kwargs)

    def _sanatize_interceptor(self, mock: str) -> pathlib.Path:
        """
        Internal method for sanatizing and validating interceptor
        """
        mock = self._path_to_mocks.joinpath(mock)

        if not mock.suffix:
            # If supplied mock-name is missing .py, add it.
            mock = mock.with_suffix(".py")

        if mock not in self._get_available_mocks():
            # If interceptor is not available raise/
            log.error(f"Requested interceptor `{mock}` is not available; check `Response.available`")
            raise InterceptorNotFound(
                f"Requested interceptor `{mock}` is not available; check `Response.available`"
            )
        return mock

    pass
