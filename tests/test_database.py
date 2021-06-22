import pytest

from pytest_response.database import ResponseDB
from pytest_response.exceptions import MalformedUrl


def test_response_db(tmp_path):
    path = tmp_path / "temp_db.json"
    db = ResponseDB(path)

    url = "https://testurl"
    data = b"Hello, this is a test."
    headers = {"Test": True}
    status = "200"

    assert db.insert(url=url, response=data, headers=headers, status=status) is None
    get_status, get_data, get_headers = db.get(url)
    assert get_status == "200"
    assert get_data == data
    assert get_headers == headers

    assert db.all()
    assert db.index()

    assert db.truncate() is None
    assert db.all() == []

    noget_status, noget_data, noget_headers = db.get("https://invalid_url")
    assert noget_status == "404"
    assert noget_data == b""
    assert noget_headers == {}

    with pytest.raises(MalformedUrl):
        db.get("invalid_url")

    db.close()
