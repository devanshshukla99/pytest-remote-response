import re

from pytest_response import response
from pytest_response.logger import log


def pytest_addoption(parser):
    """
    Pytest hook for adding cmd-line options.
    """
    parser.addoption(
        "--remote",
        dest="remote",
        action="store",
        type=str,
        default=None,
        help="Patches interceptors. --remote=[urllib|urllib3|urllib_quick|urllib3_quick|requests_quick]",
    )
    parser.addoption(
        "--remote-capture",
        dest="remote_capture",
        action="store_true",
        default=False,
        help="Capture connections requests.",
    )
    parser.addoption(
        "--remote-response",
        dest="remote_response",
        action="store_true",
        default=False,
        help="Mocks connection requests.",
    )
    parser.addoption(
        "--remote-db",
        dest="remote_db",
        action="store",
        type=str,
        default="basedata.json",
        help="Dumps the captured data to this file. --remote-db=[DUMPFILE]",
    )
    parser.addoption(
        "--remote-blocked",
        dest="remote_blocked",
        action="store_false",
        default=True,
        help="Blocks remote connection requests for all interceptors.",
    )


def pytest_configure(config):
    """
    Pytest hook for setting up monkeypatch, if ``--intercept-remote`` is ``True``
    """
    if not config.option.remote and config.option.verbose:
        print(f"Remote:{config.option.remote}")

    patch = config.option.remote
    print(f"Patch:{patch}")
    if patch:
        if config.option.remote_capture and config.option.remote_response:
            # either remote_capture or remote_response
            assert not config.option.remote_capture and config.option.remote_response
        mocks = re.split("[,]|[|]", patch)
        response.registermany(mocks)
    else:
        response.registermany(["urllib_quick", "requests_quick"])

    response.setup_database(config.option.remote_db)
    response.configure(
        remote=bool(config.option.remote_blocked),
        capture=bool(config.option.remote_capture),
        response=config.option.remote_response,
    )
    response.applyall()


# def pytest_runtest_setup(item):


# def pytest_runtest_teardown(item):


def pytest_unconfigure(config):
    """
    Pytest hook for cleaning up.
    """
    response.unapplyall()
    response.unregister()
