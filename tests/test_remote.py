import requests


def test_requests_urls():
    u = requests.get("https://www.python.org")
    assert u.status_code == 200


def test_remote(testdir):
    testdir.makepyfile(
        """
        import pytest
        from urllib.request import urlopen
        import requests
        import socket

        def test_requests_urls():
            u = requests.get("https://www.python.org")
            assert u.status_code == 200

        def test_urllib_urls():
            u = urlopen("https://www.python.org/")
            assert u.status == 200

        def test_socket():
            s = socket.socket()
            assert s.connect(("www.python.org", 80)) is None
            s.close()
        """
    )

    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
