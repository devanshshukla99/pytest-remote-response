import io

import pytest

from pytest_response.app import BaseMockResponse, Response
from pytest_response.exceptions import DatabaseNotFound, InterceptorNotFound


def test_response_obj():
    res = Response()
    assert not all([res.capture, res.remote, res.response])
    assert res.available

    assert res.register("urllib") is None
    assert list(res.registered().keys()) == ["urllib"]
    assert res.registermany(["urllib_quick", "requests_quick"]) is None
    assert list(res.registered().keys()) == ["urllib", "urllib_quick", "requests_quick"]

    res.remote = True
    assert res.remote is True

    res.capture = True
    assert res.capture is True

    res.response = True
    assert res.response is True

    res.configure(remote=False, capture=False, response=False)
    assert not all([res.capture, res.remote, res.response])

    res.unapply()
    res.post("urllib3")
    assert list(res.registered().keys()) == ["urllib", "urllib_quick", "requests_quick", "urllib3"]
    res.unpost()
    assert list(res.registered().keys()) == []


def test_response_exceptions():
    res = Response()

    with pytest.raises(InterceptorNotFound):
        res.register("invalid_interceptor")

    with pytest.raises(TypeError):
        res.remote = "Invalid"

    with pytest.raises(TypeError):
        res.capture = "Invalid"

    with pytest.raises(TypeError):
        res.response = "Invalid"

    with pytest.raises(DatabaseNotFound):
        res.insert("", b"", {}, 200)

    with pytest.raises(DatabaseNotFound):
        res.get("")


def test_basemockresponse():
    res = BaseMockResponse(200, b"Hello", headers={"Mock": True})

    assert res.code == res.status_code == res.status == res.getcode() == 200
    assert res.headers
    assert res.info()
    assert res.read()

    res.fp.seek(0)
    assert res.readline()

    res.fp.seek(0)
    buffer = io.BytesIO()
    res.readinto(buffer.getbuffer())
    res.flush()
    res.close()
