import aiohttp
from functools import wraps

from pytest_response import response
from pytest_response.exceptions import ResponseNotFound


def get_wrapper(func):
    @wraps(func)
    async def inner_func(self, *args, **kwargs):
        if response.response:
            data, headers = response.get(url=str(self._real_url))
            if not data:
                raise ResponseNotFound
            print(data[:50])
            return data.decode("utf-8")
        data = await func(self)
        if response.capture:
            response.insert(
                url=str(self._real_url), response=data.encode("utf-8"), headers=str(self._headers)
            )
        return data

    return inner_func


def install():
    _aiohttpget = aiohttp.ClientResponse.text
    naiohttpget = get_wrapper(_aiohttpget)
    response.mpatch.setattr("aiohttp.ClientResponse.text", naiohttpget)
    return


def uninstall():
    response.mpatch.undo()
    return
