def test_remote(testdir):
    testdir.makepyfile(
        """
        import requests
        from pytest_response import response
        def test_urllib3():
            url = "http://www.testingmcafeesites.com/testcat_ac.html"
            res = requests.get(url)
            assert res.status_code == 200
            assert res.content

        def test_urllib3_ssl():
            url = "https://www.python.org"
            res = requests.get(url)
            assert res.status_code == 200
            assert res.content

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """
    )
    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(failed=3)

    result = testdir.runpytest("-q", "--remote", "-p", "no:warnings")
    result.assert_outcomes(passed=2, failed=1)

    result = testdir.runpytest("-q", "--remote", "--remote-capture", "-p", "no:warnings")
    result.assert_outcomes(passed=3)

    result = testdir.runpytest("-q", "--remote", "--response", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
