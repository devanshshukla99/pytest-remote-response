import pathlib
from urllib.parse import urljoin, urlparse
from pytest_response.logger import log
from pytest_response.database import database
import importlib.util


class Controller:
    """
    Internal controller for interceptors.
    """

    def __init__(self, capture=True):
        self.capture = capture
        self.url = None
        self.host = None
        self.https = False
        self.headers = {}
        self.db = None

    def _setup_database(self, path):
        """
        Internal method for setting up the database.
        """
        self.db = database(path)

    def build_url(self, host, url, https=False):
        """
        Internal controller method for building urls.
        """
        self.url = url
        self.host = host
        self.https = https
        _scheme = "https://" if https else "http://"
        _url = "".join([_scheme, host])
        self.url = urljoin(_url, url)
        if self._validate_url(_url):
            return self.url
        raise MalformedUrl(f"URL '{_url}' is invalid")

    def _validate_url(self, value):
        """
        Internal method for validating a URL.
        """
        result = urlparse(value)
        return all([result.scheme, result.netloc])

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


class app:
    """
    Controlling and configuration application for `pytest_response`
    """

    def __init__(
        self, path="interceptors", capture=True, database="db.json", log_level="debug"
    ) -> None:
        log.setLevel(log_level.upper())
        control.capture = self._capture = capture
        self._basepath = pathlib.Path(__file__).parent
        self._db_path = self._basepath.joinpath(database)
        self._path_to_mocks = self._basepath.joinpath(path)
        self.available_mocks = list(self._get_available_mocks())
        self._registered_mocks = []
        self._registered_libs = []
        control._setup_database(self._db_path)
        # self.control = control(capture)

    def _get_available_mocks(self):
        """
        Internal method to get available interceptors.
        """
        return self._path_to_mocks.rglob("*.py")

    def registered(self):
        """
        Returns registeres modules.
        """
        return self._registered_mocks

    def register(self, mock) -> None:
        """
        Registers interceptor modules; applies using `pytest_response.app.applies`
        """
        mock = self._path_to_mocks.joinpath(mock)
        if not mock.suffix:
            mock = mock.with_suffix(".py")
        if mock in self._get_available_mocks():
            log.info(f"{mock.name} registered")
            self._registered_mocks.append(mock)
            return True
        return False

    def unregister(self) -> None:
        """
        Deactivates interceptor modules.
        """
        try:
            for lib in self._registered_libs:
                lib.uninstall()
                log.debug(f"{lib.__name__} unregistered")
        except Exception:
            raise

    def apply(self) -> bool:
        """
        Activates intercepter modules.
        """
        for mock_path in self._registered_mocks:
            log.debug(f"{mock_path.name} applied")
            spec = importlib.util.spec_from_file_location(
                mock_path.name, str(mock_path)
            )
            mock_lib = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mock_lib)
            self._registered_libs.append(mock_lib)
            mock_lib.install()
        return True

    pass


class MalformedUrl(Exception):
    """
    Exception raised when a malformed URL is encountered.
    """

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

    pass


control = Controller()
