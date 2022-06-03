import pytest


@pytest.fixture
def testcode():
    return """
        import aiohttp
        import pytest
        import asyncio
        from pytest_response import response

        @pytest.fixture(scope="function")
        def event_loop():
            loop = asyncio.new_event_loop()
            yield loop
            loop.close()

        @response.activate("aiohttp")
        def test_aiohttp_capture(event_loop):
            async def async_whats_this():
                url = "http://www.testingmcafeesites.com/testcat_ac.html"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        status = response.status
                        data = await response.text()
                        assert status == 200
                        assert data
            event_loop.run_until_complete(async_whats_this())

        @response.activate("aiohttp")
        def test_aiohttp_capture_ssl(event_loop):
            async def async_whats_this():
                url = "https://www.python.org"
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        status = response.status
                        data = await response.text()
                        assert status == 200
                        assert data
            event_loop.run_until_complete(async_whats_this())

        def test_database():
            assert response.db.index() == ["http://www.testingmcafeesites.com/testcat_ac.html",
                                           "https://www.python.org"]
        """


def test_remote_block(testdir, testcode):
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
