import json
import socket
from urllib.request import urlopen

import pytest
import requests


@pytest.fixture(scope="function")
def _intercept_test_skip(request):
    """
    Pytest fixture for enforcing skip conditions
    """
    if not hasattr(request.config.option, "intercept_remote"):
        pytest.skip("pytest-intercept-remote plugin not available")
    if request.config.option.intercept_remote:
        pytest.skip("rerun without --intercept-remote")


@pytest.mark.usefixtures("_intercept_test_skip")
def test_requests_urls():
    u = requests.get("https://www.python.org")
    assert u.status_code == 200


@pytest.mark.usefixtures("_intercept_test_skip")
def test_urllib_urls():
    u = urlopen("https://www.python.org/")
    assert u.status == 200


@pytest.mark.usefixtures("_intercept_test_skip")
def test_socket():
    s = socket.socket()
    assert s.connect(("www.python.org", 80)) is None
    s.close()


@pytest.mark.usefixtures("_intercept_test_skip")
def test_remote(testdir):
    testdir.makepyfile(
        """
        import pytest
        from urllib.request import urlopen
        import requests
        import socket

        def test_requests_urls():
            u = requests.get("https://www.python.org")
            assert u.status_code == 200

        def test_urllib_urls():
            u = urlopen("https://www.python.org/")
            assert u.status == 200

        def test_socket():
            s = socket.socket()
            assert s.connect(("www.python.org", 80)) is None
            s.close()

        def test_dump(intercepted_urls):
            assert intercepted_urls == {"urls_urllib": [], "urls_requests": [], "urls_socket": []}
        """
    )

    result = testdir.runpytest(
        "-q", "-p", "no:warnings", "-o", "intercept_dump_file=test_urls.json"
    )
    result.assert_outcomes(passed=4)


@pytest.mark.usefixtures("_intercept_test_skip")
def test_intercept_remote(testdir):
    """
    Testing intercept session.
    """
    testdir.makepyfile(
        """
        import pytest
        from urllib.request import urlopen
        import requests
        import socket

        def test_requests_urls():
            u = requests.get("https://www.python.org")
            assert u.status_code == 200

        def test_urllib_urls():
            u = urlopen("https://www.python.org/")
            assert u.status == 200

        def test_socket():
            s = socket.socket()
            assert s.connect(("www.python.org", 80)) is None
            s.close()

        def test_dump(intercepted_urls):
            assert intercepted_urls == {"urls_urllib": ["https://www.python.org/"],
                                        "urls_requests": ["https://www.python.org/"],
                                        "urls_socket": [("www.python.org", 80)]}
        """
    )

    result = testdir.runpytest(
        "-q",
        "-p",
        "no:warnings",
        "--intercept-remote",
        "-o",
        "intercept_dump_file=test_urls.json",
    )
    result.assert_outcomes(xfailed=3, passed=1)


@pytest.mark.usefixtures("_intercept_test_skip")
def test_remote_status(testdir):
    """
    Test for remote status.
    """
    _dump_data = json.dumps(
        {
            "urls_urllib": [
                "https://www.python.org/",
                "https://www.python.org/invalidpage_404test",
            ],
            "urls_requests": [
                "https://www.python.org/",
                "https://www.python.org/invalidpage_404test",
            ],
            "urls_socket": [("www.python.org", 80)],
        }
    )
    testdir.maketxtfile(_dump_data)

    result = testdir.runpytest(
        "-q",
        "-p",
        "no:warnings",
        "--remote-status",
        "-o",
        "intercept_dump_file=test_remote_status.txt",
    )
    result.assert_outcomes(passed=3, xfailed=2)


@pytest.mark.usefixtures("_intercept_test_skip")
def test_fixtures(testdir):
    """
    Testing skip conditions
    """
    testdir.makepyfile(
        """
        import pytest
        @pytest.mark.usefixtures("intercept_skip_conditions")
        def test_skip_conditions():
            assert True
        """
    )
    result = testdir.runpytest("-q", "-p", "no:warnings")
    result.assert_outcomes(skipped=1)
    result = testdir.runpytest("-q", "-p", "no:warnings", "--remote-status=only")
    result.assert_outcomes(skipped=3)
    result = testdir.runpytest("-q", "-p", "no:warnings", "--intercept-remote")
    result.assert_outcomes(skipped=1)
