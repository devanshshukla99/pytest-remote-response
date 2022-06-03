import pytest
from pytest_response.logger import log


@pytest.fixture
def testcode():
    return """
        import urllib3
        from pytest_response import response

        @response.activate("urllib3")
        def test_urllib3():
            http = urllib3.PoolManager()
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = http.request("GET", url)
            assert res.status == 200
            assert res.data

        @response.activate("urllib3")
        def test_urllib3_ssl():
            http = urllib3.PoolManager()
            url = "https://www.python.org"
            res = http.request("GET", url)
            assert res.status == 200
            assert res.data

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """


def test_remote_blocked(pytester, testcode):
    pytester.makepyfile(testcode)

    result = pytester.runpytest("-q", "--remote-block", "-p", "no:warnings")
    result.assert_outcomes(failed=3)


def test_remote_connection(pytester, testcode):
    pytester.makepyfile(testcode)

    result = pytester.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp(pytester, testcode):
    log.debug(pytester)
    pytester.makepyfile(testcode)

    result = pytester.runpytest("-q", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = pytester.runpytest("-q", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
