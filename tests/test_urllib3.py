import pytest


@pytest.fixture
def testcode():
    return """
        import urllib3
        from pytest_response import response

        def test_urllib3():
            http = urllib3.PoolManager()
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = http.request("GET", url)
            assert res.status == 200
            assert res.data

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


def test_remote_blocked(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote=urllib3", "--remote-blocked", "-p", "no:warnings")
    result.assert_outcomes(failed=3)


def test_remote_connection(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote=urllib3", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote=urllib3", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--remote=urllib3", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)


def test_remote_connection_full(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote=urllib3_full", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp_full(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote=urllib3_full", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--remote=urllib3_full", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
