import pytest

from pytest_response.exceptions import (  # isort: skip
    DatabaseNotFound,
    InterceptorNotFound,
    MalformedUrl,
    RemoteBlockedError,
    ResponseNotFound,
)


@pytest.mark.parametrize(
    "exec", [RemoteBlockedError, InterceptorNotFound, ResponseNotFound, MalformedUrl, DatabaseNotFound]
)
def test_exceptions(exec):
    with pytest.raises(exec):
        raise exec
