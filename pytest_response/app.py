import os.path
import pathlib
from urllib.parse import urljoin, urlparse
from .logger import _init_log
import importlib


class control:
    def __init__(self, capture=True):
        self.capture = capture
        self.url = None
        self.host = None
        self.https = False
        self.headers = {}

    def build_url(self, host, url, https=False):
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
        result = urlparse(value)
        return all([result.scheme, result.netloc])

    pass


class app:
    def __init__(self, path="interceptors", capture=False, log_level="debug") -> None:
        self.log = _init_log(log_level)
        self._capture = capture
        self._basepath = pathlib.Path(__file__).parent
        self._path_to_mocks = pathlib.Path(self._basepath, path)
        self._available_mocks = list(self._get_available_mocks())
        self._registered_mocks = []
        self.control = control(capture)

    def _get_available_mocks(self):
        return self._path_to_mocks.rglob('*.py')

    def registered(self):
        return self._registered_mocks

    def register(self, mock) -> None:
        mock = pathlib.Path(self._path_to_mocks, mock)
        if not mock.suffix:
            mock.with_suffix(".py")
        if mock in self._get_available_mocks():
            print("Registered!")
            self._registered_mocks.append(mock)
            return True
        return False

    def apply(self) -> bool:
        for mock_path in self._registered_mocks:
            mock_lib = importlib.import_module(mock_path)
            mock_lib.install()


class MalformedUrl(Exception):
    """
    Exception raised when a malformed URL is encountered.
    """

    def __init__(self, reason):
        self.reason = reason
        super().__init__(reason)

    pass
