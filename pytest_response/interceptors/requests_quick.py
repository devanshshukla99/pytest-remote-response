from functools import wraps

import requests
import urllib3

from pytest_response import response
from pytest_response.exceptions import RemoteBlockedError, ResponseNotFound
from pytest_response.logger import log


def requests_wrapper(func):
    @wraps(func)
    def inner_func(url, params=None, **kwargs):
        if not response.remote:
            log.error(f"RemoteBlockedError remote:{response.remote}")
            raise RemoteBlockedError
        if response.response:
            data, headers = response.get(url=url)
            if not data:
                log.error(f"Response not found url:{url}")
                raise ResponseNotFound
            return MockResponse(data, headers)
        _ = func(url, params, **kwargs)
        if not response.capture:
            return _
        data = _.content
        response.insert(url=url, response=data, headers=dict(_.headers))
        return _

    return inner_func


class MockResponse:
    def __init__(self, data, headers={}):
        self.status = self.code = self.status_code = 200
        self.msg = self.reason = "OK"
        self.headers = urllib3.response.HTTPHeaderDict(headers)
        self.will_close = True
        self.content = data
        self._fp = None

    def read(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.read
        """
        return self._fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readline
        """
        return self._fp.readline(*args, **kwargs)

    def readinto(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readinto
        """
        return self._fp.readinto(*args, **kwargs)

    def close(self):
        if hasattr(self, "_fp"):
            self._fp.close()

    pass


def install_opener():
    u3open = requests.get
    nurlopen = requests_wrapper(u3open)
    response.mpatch.setattr("requests.get", nurlopen)
    return


def uninstall_opener():
    response.mpatch.undo()
    # response.mpatch.setattr("urllib.request.urlopen", )


install = install_opener
uninstall = uninstall_opener
