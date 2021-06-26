from functools import wraps

import requests
import urllib3

from pytest_response import response
from pytest_response.app import BaseMockResponse
from pytest_response.exceptions import RemoteBlockedError, ResponseNotFound
from pytest_response.logger import log

__all__ = ["MockResponse", "requests_wrapper", "install", "uninstall"]


def requests_wrapper(func):
    @wraps(func)
    def inner_func(url, params=None, **kwargs):
        if not response.remote:
            log.error(f"RemoteBlockedError remote:{response.remote}")
            raise RemoteBlockedError
        if response.response:
            status, data, headers = response.get(url=url)
            if not data:
                log.error(f"Response not found url:{url}")
                raise ResponseNotFound
            return MockResponse(status, data, headers)
        _ = func(url, params, **kwargs)
        if not response.capture:
            return _
        data = _.content
        response.insert(url=url, response=data, headers=dict(_.headers), status=_.status_code)
        return _

    return inner_func


class MockResponse(BaseMockResponse):
    def __init__(self, status, data, headers={}):
        headers = urllib3.response.HTTPHeaderDict(headers)
        self.content = data
        super().__init__(status, data, headers)

    pass


def install_opener():
    u3open = requests.get
    nurlopen = requests_wrapper(u3open)
    response.mpatch.setattr("requests.get", nurlopen)
    return


def uninstall_opener():
    response.mpatch.undo()


install = install_opener
uninstall = uninstall_opener
