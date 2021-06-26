import re

from pytest_response import response


def pytest_addoption(parser):
    """
    Pytest hook for adding cmd-line options.

    Adds ``--remote``, ``--remote-capture``, ``--remote-response``, ``--remote-db`` and ``--remote-blocked``
    options to pytest.
    """
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
    Pytest hook for setting up :class:`pytest_response.app.Response`
    """
    if config.option.remote_capture and config.option.remote_response:
        # either remote_capture or remote_response
        assert not config.option.remote_capture and config.option.remote_response

    if config.option.remote_capture or config.option.remote_response:
        response.setup_database(config.option.remote_db)
        response.configure(
            remote=bool(config.option.remote_blocked),
            capture=bool(config.option.remote_capture),
            response=config.option.remote_response,
        )


def pytest_unconfigure():
    """
    Pytest hook for cleaning up.
    """
    if config.option.remote_capture or config.option.remote_response:
        response.unpost()
