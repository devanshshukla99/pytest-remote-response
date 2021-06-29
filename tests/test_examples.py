def test_examples(testdir):
    testdir.makepyfile(
        """
        import pytest
        from pytest_response import response
        from pytest_response.exceptions import RemoteBlockedError

        def test_block_urllib():
            with pytest.raises(RemoteBlockedError):
                from examples import block_urllib  # noqa
            return

        def test_capture_requests():
            from examples import capture_requests  # noqa
            assert response.db.index() == ["https://www.python.org"]
            return

        def test_response_urllib3():
            from examples import response_urllib3  # noqa
            return
        """
    )

    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=3)
