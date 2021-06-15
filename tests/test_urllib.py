def test_remote_block(testdir):
    testdir.makepyfile(
        """
        import urllib.request
        from pytest_response import response
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """
    )
    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(failed=3)


def test_remote_connection(testdir):
    testdir.makepyfile(
        """
        import urllib.request
        from pytest_response import response
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """
    )
    result = testdir.runpytest("-q", "--remote=urllib_quick|requests_quick", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp(testdir):
    testdir.makepyfile(
        """
        import urllib.request
        from pytest_response import response
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """
    )
    result = testdir.runpytest(
        "-q", "--remote=urllib_quick|requests_quick", "--remote-capture", "-p", "no:warnings"
    )
    result.assert_outcomes(passed=3)

    result = testdir.runpytest(
        "-q", "--remote=urllib_quick|requests_quick", "--remote-response", "-p", "no:warnings"
    )
    result.assert_outcomes(passed=3)


def test_remote_connection_full(testdir):
    testdir.makepyfile(
        """
        import urllib.request
        from pytest_response import response
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """
    )
    result = testdir.runpytest("-q", "--remote=urllib|urllib3", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)


def test_remote_capresp_full(testdir):
    testdir.makepyfile(
        """
        import urllib.request
        from pytest_response import response
        def test_urllib_capture():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_urllib_capture_ssl():
            url = "https://www.python.org"
            res = urllib.request.urlopen(url)
            assert res.status == 200
            assert res.read()

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """
    )
    result = testdir.runpytest("-q", "--remote=urllib|urllib3", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--remote=urllib|urllib3", "--remote-response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
