from functools import wraps
from urllib.parse import urljoin

import urllib3

from pytest_response import response
from pytest_response.app import BaseMockResponse
from pytest_response.exceptions import RemoteBlockedError, ResponseNotFound
from pytest_response.logger import log

__all__ = ["MockResponse", "urlopen_wrapper", "install", "uninstall"]


def _build_url(scheme, host, url):
    _scheme_host = "://".join([scheme, host])
    return urljoin(_scheme_host, url)


def urlopen_wrapper(func):
    """
    Wrapper for :meth:`urllib3.HTTPConnectionPool.urlopen`
    """

    @wraps(func)
    def inner_func(self, method, url, timeout=5, *args, **kwargs):
        kwargs["timeout"] = timeout
        _url = _build_url(self.scheme, self.host, url)
        log.debug(f"Intercepting call to {_url}")
        if not response.remote:
            raise RemoteBlockedError
        if response.response:
            status, data, headers = response.get(url=_url)
            if not data:
                log.error(f"Response not found url:{_url}")
                raise ResponseNotFound
            return MockResponse(status, data, headers)
        _ = func(self, method, url, *args, **kwargs)
        if not response.capture:
            return _
        data = _.data
        response.insert(url=_url, response=data, headers=dict(_.headers), status=_.status)
        return _

    return inner_func


class MockResponse(BaseMockResponse):
    def __init__(self, status, data, headers={}):
        headers = urllib3.response.HTTPHeaderDict(headers)
        self.data = data
        super().__init__(status, data, headers)

    def get_redirect_location(self, *args, **kwargs):
        return ""


def install_opener():
    """
    Method to monkey patch the library call with the wrapped one.
    """
    u3open = urllib3.connectionpool.HTTPConnectionPool.urlopen
    nurlopen = urlopen_wrapper(u3open)
    response.mpatch.setattr("urllib3.connectionpool.HTTPConnectionPool.urlopen", nurlopen)
    return


def uninstall_opener():
    """
    Method to undo all monkey patches.
    """
    response.mpatch.undo()
    return


install = install_opener
uninstall = uninstall_opener
