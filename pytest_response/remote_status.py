import json
import socket
from os.path import isfile
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

import pytest
import requests

__all__ = ["test_urls_urllib", "test_urls_requests", "test_urls_socket"]


def pytest_generate_tests(metafunc):
    """
    Pytest hook for generating tests for all intercepted urls.
    """
    funcarglist = [None]

    if hasattr(metafunc.config.option, "intercept_remote"):
        intercept_remote = metafunc.config.option.intercept_remote
        intercept_dump_file = metafunc.config.getini("intercept_dump_file")
        funcarglist = {}
        if isfile(intercept_dump_file) and not intercept_remote:
            with open(metafunc.config.getini("intercept_dump_file")) as fd:
                funcarglist = json.load(fd)
        funcarglist = funcarglist.get(metafunc.function.__name__.replace("test_", ""), [None]) or [None]
        metafunc.parametrize("intercept_url", funcarglist, indirect=True)


@pytest.mark.usefixtures("intercept_skip_conditions")
def test_urls_urllib(intercept_url):
    """
    Test for urls using urllib module.
    """
    try:
        res = urlopen(intercept_url)
        assert res.status == 200
    except (HTTPError, URLError) as e:
        pytest.xfail(f"URL unreachable, status:{e.reason}")


@pytest.mark.usefixtures("intercept_skip_conditions")
def test_urls_requests(intercept_url):
    """
    Test for urls using requests module.
    """
    res = requests.get(intercept_url)
    status = res.status_code
    if status != 200:
        pytest.xfail(f"URL unreachable, status:{status}")
    assert res.status_code == 200


@pytest.mark.usefixtures("intercept_skip_conditions")
def test_urls_socket(intercept_url):
    """
    Test for urls using socket.
    """
    sock = socket.socket(socket.AF_INET)
    if len(intercept_url) == 4:
        sock = socket.socket(socket.AF_INET6)
    try:
        assert sock.connect(tuple(intercept_url)) is None
    except ConnectionRefusedError:
        pytest.xfail(f"URL unreachable, url:({intercept_url[0]},{intercept_url[1]})")
    finally:
        sock.close()
