def test_examples(pytester):
    pytester.makepyfile(
        """
        import pytest
        from base64 import b64encode

        from pytest_response import response
        from pytest_response.exceptions import RemoteBlockedError

        def test_block_urllib():
            with pytest.raises(RemoteBlockedError):
                from examples import block_urllib  # noqa
            return

        def test_capture_requests():
            from examples import capture_requests  # noqa
            assert response.db.index() == [b64encode(b"https://www.python.org").decode()]
            return

        def test_response_urllib3():
            from examples import response_urllib3  # noqa
            return

        def test_response_decorator_urllib3():
            from examples import response_decorator_urllib3  # noqa
            return

        def test_insert_get_database():
            from examples import insert_get_database  # noqa
            return
        """
    )

    result = pytester.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(passed=5)
