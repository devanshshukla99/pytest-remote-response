from pytest_response.database import ResponseDB


def test_response_db(tmp_path):
    path = tmp_path / "temp_db.json"
    db = ResponseDB(path)

    url = "testurl"
    data = b"Hello, this is a test."
    headers = {"Test": True}

    assert db.insert(url=url, response=data, headers=headers) is None
    get_data, get_headers = db.get(url)
    assert get_data == data
    assert get_headers == headers

    assert db.all()
    assert db.index()

    assert db.truncate() is None
    assert db.all() == []

    noget_data, noget_headers = db.get("invalid_url")
    assert noget_data == b""
    assert noget_headers == {}

    db.close()
