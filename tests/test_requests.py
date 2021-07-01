import pytest


@pytest.fixture
def testcode():
    return """
        import requests
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
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """


def test_remote_blocked(testdir, testcode):
    testdir.makepyfile(testcode)
    result = testdir.runpytest("-q", "--response", "--remote-blocked", "-p", "no:warnings")
    result.assert_outcomes(failed=3)


def test_remote_connection(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--response", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--response", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--response", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
