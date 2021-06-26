import pytest


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


@pytest.fixture
def testcode_full():
    return """
        import urllib3
        from pytest_response import response

        @response.activate("urllib3_full")
        def test_urllib3():
            http = urllib3.PoolManager()
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = http.request("GET", url)
            assert res.status == 200
            assert res.data

        @response.activate("urllib3_full")
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

    result = testdir.runpytest("-q", "--remote-blocked", "-p", "no:warnings")
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


def test_remote_connection_full(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp_full(testdir, testcode):
    testdir.makepyfile(testcode)

    result = testdir.runpytest("-q", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
