import pathlib
from pytest_response.logger import log
from pytest_response.database import ResponseDB
import importlib.util


# class Controller:
#     """
#     Internal controller for interceptors.
#     """

#     def __init__(
#         self,
#         capture: Optional[Type[bool]] = False,
#         response: Optional[Type[bool]] = False,
#         remote: Optional[Type[bool]] = False,
#     ):
#         self.capture = capture
#         self.response = response
#         self.remote = remote
#         self.url = None
#         self.host = None
#         self.https = False
#         self.headers = {}
#         self.db = None

#     def _setup_database(self, path: Type[str]):
#         """
#         Internal method for setting up the database.
#         """
#         self.db = database(path)

#     def build_url(
#         self, host: Type[str], url: Type[str], https: Optional[Type[bool]] = False
#     ):
#         """
#         Internal controller method for building urls.
#         """
#         self.url = url
#         self.host = host
#         self.https = https
#         _scheme = "https://" if https else "http://"
#         _url = "".join([_scheme, host])
#         self.url = urljoin(_url, url)
#         if self._validate_url(_url):
#             return self.url
#         raise MalformedUrl(f"URL '{_url}' is invalid")

#     def _validate_url(self, value: Type[str]):
#         """
#         Internal method for validating a URL.
#         """
#         result = urlparse(value)
#         return all([result.scheme, result.netloc])

#     def insert(self, *args, **kwargs):
#         """
#         Wrapper function for `pytest_response.database.db.insert`
#         """
#         return self.db.insert(*args, **kwargs)

#     def get(self, *args, **kwargs):
#         """
#         Wrapper function for `pytest_response.database.db.get`
#         """
#         return self.db.get(*args, **kwargs)

#     pass


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
        log.info(
            "<------------------------------------------------------------------->"
        )
        self._basepath = pathlib.Path(__file__).parent
        self._db_path = self._basepath.joinpath(database)
        self._path_to_mocks = self._basepath.joinpath(path)
        self._available_mocks = list(self._get_available_mocks())
        self._registered_mocks = []

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
        mock = self._path_to_mocks.joinpath(mock)
        if not mock.suffix:
            mock = mock.with_suffix(".py")
        if mock not in self._get_available_mocks():
            raise InterceptorNotFound(
                f"Requested interceptor `{mock}` is not available; check `available()`"
            )
        spec = importlib.util.spec_from_file_location(mock.name, str(mock))
        mock_lib = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mock_lib)
        self._registered_mocks.append(mock_lib)
        log.info(f"{mock.name} registered")
        return

    def unregister(self) -> None:
        """
        Deactivates interceptor modules.
        """
        try:
            for lib in self._registered_mocks:
                lib.uninstall()
                log.debug(f"{lib.__name__} unregistered")
            self._registered_mocks = []
        except Exception:
            raise

    def apply(self) -> bool:
        """
        Activates intercepter modules.
        """
        for mock_lib in self._registered_mocks:
            mock_lib.install()
        log.debug("interceptors applied")
        return

    def unapply(self) -> None:
        """
        Un-applies interceptor modules.
        """
        for mock_lib in self._registered_mocks:
            mock_lib.uninstall()
        log.debug("interceptors unapplied")

    def insert(self, *args, **kwargs):
        """
        Wrapper function for `pytest_response.database.db.insert`
        """
        return self.db.insert(*args, **kwargs)

    def get(self, *args, **kwargs):
        """
        Wrapper function for `pytest_response.database.db.get`
        """
        return self.db.get(*args, **kwargs)

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
