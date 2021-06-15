import io
import urllib.request
from functools import wraps

from pytest_response import response
from pytest_response.logger import log


class RemoteBlockedError(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(RemoteBlockedError, self).__init__("A test tried to connect to internet.")


class ResponseNotFound(RuntimeError):
    def __init__(self, *args, **kwargs):
        super(ResponseNotFound, self).__init__("Response is not available; try capturing first.")


def urlopen_wrapper(func):
    @wraps(func)
    def inner_func(url, *args, **kwargs):
        if not response.remote:
            raise RemoteBlockedError
        if response.response:
            data, headers = response.get(url=url)
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


class MockResponse:
    def __init__(self, data, headers={}):
        self.status = self.code = 200
        self.msg = self.reason = "OK"
        self.headers = headers
        self.will_close = True
        if not isinstance(data, io.BytesIO):
            data = io.BytesIO(data)
        self.fp = data
        self.will_close = True

    def flush(self):
        self.fp.flush()

    def info(self):
        return {}

    def read(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.read
        """
        return self.fp.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readline
        """
        return self.fp.readline(*args, **kwargs)

    def readinto(self, *args, **kwargs):
        """
        Wrapper for _io.BytesIO.readinto
        """
        return self.fp.readinto(*args, **kwargs)

    def __exit__(self):
        """
        Method for properly closing resources.
        """
        if hasattr(self, "fp"):
            self.fp.close()

    def close(self):
        if hasattr(self, "fp"):
            self.fp.close()

    pass


def install_opener():
    log.error(":INSTALLED")
    uopen = urllib.request.urlopen
    nurlopen = urlopen_wrapper(uopen)
    response.mpatch.setattr("urllib.request.urlopen", nurlopen)
    return


def uninstall_opener():
    response.mpatch.undo()
    # response.mpatch.setattr("urllib.request.urlopen", )


install = install_opener
uninstall = uninstall_opener
