import pytest


@pytest.fixture
def testcode():
    return """
        import requests
        from base64 import b64encode

        from pytest_response import response

        @response.activate("requests")
        def test_requests():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = requests.get(url)
            assert res.status_code == 200
            assert res.content

        @response.activate("requests")
        def test_requests_ssl():
            url = "https://www.python.org"
            res = requests.get(url)
            assert res.status_code == 200
            assert res.content

        def test_database():
            assert response.db.index() == [b64encode(b"http://www.testingmcafeesites.com/testcat_ac.html").decode(),
                                           b64encode(b"https://www.python.org").decode()]
        """


def test_remote_blocked(testdir, testcode):
    testdir.makepyfile(testcode)
    result = testdir.runpytest("-q", "--remote-block", "-p", "no:warnings")
    result.assert_outcomes(failed=3)


def test_remote_connection(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
