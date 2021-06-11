# flake8: noqa
from pytest_response._version import version as __version__
from pytest_response.app import Response

response = Response(capture=False, remote=False, response=False)

__all__ = [response]
