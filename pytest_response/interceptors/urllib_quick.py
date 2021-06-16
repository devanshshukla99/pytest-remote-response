import io
import urllib.request
from functools import wraps

from pytest_response import response
from pytest_response.app import BaseMockResponse
from pytest_response.exceptions import RemoteBlockedError, ResponseNotFound
from pytest_response.logger import log


def urlopen_wrapper(func):
    @wraps(func)
    def inner_func(url, *args, **kwargs):
        if not response.remote:
            log.error(f"RemoteBlockedError remote:{response.remote}")
            raise RemoteBlockedError
        if response.response:
            data, headers = response.get(url=url)
            if not data:
                log.error(f"Response not found url:{url}")
                raise ResponseNotFound
            return MockResponse(data, headers)

        _ = func(url, *args, **kwargs)
        if not response.capture:
            return _
        data = _.fp.read()
        _.fp = io.BytesIO(data)
        headers = _.headers
        response.insert(url=url, response=data, headers=dict(headers))
        return _

    return inner_func


class MockResponse(BaseMockResponse):
    def __init__(self, data, headers={}):
        super().__init__(data, headers)

    pass


def install_opener():
    uopen = urllib.request.urlopen
    nurlopen = urlopen_wrapper(uopen)
    response.mpatch.setattr("urllib.request.urlopen", nurlopen)
    return


def uninstall_opener():
    response.mpatch.undo()


install = install_opener
uninstall = uninstall_opener
