import io
from functools import wraps
from urllib.parse import urljoin

import urllib3

from pytest_response import response
from pytest_response.logger import log
from pytest_response.exceptions import RemoteBlockedError, ResponseNotFound


def _build_url(scheme, host, url):
    _scheme_host = "://".join([scheme, host])
    return urljoin(_scheme_host, url)


def urlopen_wrapper(func):
    @wraps(func)
    def inner_func(self, method, url, *args, **kwargs):
        _url = _build_url(self.scheme, self.host, url)
        if not response.remote:
            raise RemoteBlockedError
        if response.response:
            data, headers = response.get(url=_url)
            if not data:
                log.error(f"Response not found url:{_url}")
                raise ResponseNotFound
            print(type(headers))
            log.error(headers)
            return MockResponse(data, headers)
        _ = func(self, method, url, *args, **kwargs)
        if not response.capture:
            return _
        print(_.headers)
        data = _._fp.read()
        _._fp = io.BytesIO(data)
        response.insert(url=_url, response=data, headers=dict(_.headers))
        return _

    return inner_func


class MockResponse:
    def __init__(self, data, headers={}):
        self.status = self.code = 200
        self.msg = self.reason = "OK"
        self.headers = urllib3.response.HTTPHeaderDict(headers)
        self.will_close = True
        if not isinstance(data, io.BytesIO):
            data = io.BytesIO(data)
        self._fp = data
        self.will_close = True

    def flush(self):
        self._fp.flush()

    def info(self):
        return {}

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


# class MockHeaders(MutableMapping):
#     def __init__(self, default_headers={""}, *args, **kwargs):
#         self.store = dict()
#         self.update(dict(*args, **kwargs))

#     def __repr__(self):
#         return str(self.store)

#     def __getitem__(self, key):
#         return self.store[key]

#     def __setitem__(self, key, value):
#         self.store[key] = value

#     def __delitem__(self, key):
#         del self.store[key]

#     def __iter__(self):
#         return iter(self.store)

#     def __len__(self):
#         return len(self.store)

#     pass


def install_opener():
    u3open = urllib3.connectionpool.HTTPConnectionPool.urlopen
    nurlopen = urlopen_wrapper(u3open)
    response.mpatch.setattr("urllib3.connectionpool.HTTPConnectionPool.urlopen", nurlopen)
    log.error("MPATCHED")
    return


def uninstall_opener():
    response.mpatch.undo()
    # response.mpatch.setattr("urllib.request.urlopen", )


install = install_opener
uninstall = uninstall_opener
