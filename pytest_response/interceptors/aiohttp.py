from functools import wraps

import aiohttp

from pytest_response import response
from pytest_response.app import BaseMockResponse
from pytest_response.exceptions import RemoteBlockedError, ResponseNotFound

__all__ = ["MockResponse", "create_wrapper", "get_wrapper", "install", "uninstall"]


class MockResponse(BaseMockResponse):
    def __init__(self, status, data, headers={}):
        self.data = data
        super().__init__(status, b"", headers)

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs):
        pass

    async def text(self):
        return self.data

    pass


def create_wrapper(func):
    """
    Wrapper for :meth:`aiohttp.ClientResponse.text`
    """

    @wraps(func)
    def inner_func(self, url, *args, **kwargs):
        if not response.remote:
            raise RemoteBlockedError
        if response.response:
            status, data, headers = response.get(url=str(url))
            # self.status = status
            if not data:
                raise ResponseNotFound
            return MockResponse(200, data, headers)
        return func(self, url, *args, **kwargs)

    return inner_func


def get_wrapper(func):
    """
    Wrapper for :meth:`aiohttp.ClientSession.get`
    """

    @wraps(func)
    async def inner_func(self, *args, **kwargs):
        if not response.remote:
            raise RemoteBlockedError
        data = await func(self)
        if response.capture:
            response.insert(
                url=str(self._real_url),
                response=data.encode("utf-8"),
                headers=str(dict(self._raw_headers)),
                status=self.status,
            )
        return data

    return inner_func


def install():
    """
    Method to monkey patch the library call with the wrapped one.
    """
    _aiohttpget = aiohttp.ClientResponse.text
    naiohttpget = get_wrapper(_aiohttpget)

    _create_aio = aiohttp.ClientSession.get
    ncreate_aio = create_wrapper(_create_aio)

    response.mpatch.setattr("aiohttp.ClientSession.get", ncreate_aio)
    response.mpatch.setattr("aiohttp.ClientResponse.text", naiohttpget)
    return


def uninstall():
    """
    Method to undo all monkey patches.
    """
    response.mpatch.undo()
    return
