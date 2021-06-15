import pytest

from pytest_response.exceptions import InterceptorNotFound, MalformedUrl, RemoteBlockedError, ResponseNotFound


@pytest.mark.parametrize("exec", [RemoteBlockedError, InterceptorNotFound, ResponseNotFound, MalformedUrl])
def test_exceptions(exec):
    with pytest.raises(exec):
        raise exec
