import pytest


@pytest.fixture
def testcode():
    return """
        import urllib.request
        from pytest_response import response

        @response.activate("urllib")
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        @response.activate("urllib")
        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """


@pytest.fixture
def testcode_full():
    return """
        import urllib.request
        from pytest_response import response

        @response.activate("urllib_full")
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        @response.activate("urllib_full")
        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """


def test_remote_block(testdir, testcode):
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


def test_remote_connection_full(testdir, testcode):
    testdir.makepyfile(testcode)
    result = testdir.runpytest("-q", "--response", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp_full(testdir, testcode):
    testdir.makepyfile(testcode)
    result = testdir.runpytest("-q", "--response", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--response", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
