import pytest


@pytest.fixture
def testcode():
    return """
        import urllib.request
        from base64 import b64encode

        from pytest_response import response

        response.unapply()

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
            assert response.db.index() == [b64encode(b"http://www.testingmcafeesites.com/testcat_ac.html").decode(),
                                           b64encode(b"https://www.python.org").decode()]
        """


def test_remote_block(pytester, testcode):
    pytester.makepyfile(testcode)
    result = pytester.runpytest("-q", "--remote-block", "-p", "no:warnings")
    result.assert_outcomes(failed=3)


def test_remote_connection(pytester, testcode):
    pytester.makepyfile(testcode)
    result = pytester.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp(pytester, testcode):
    pytester.makepyfile(testcode)
    result = pytester.runpytest("-q", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = pytester.runpytest("-q", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
