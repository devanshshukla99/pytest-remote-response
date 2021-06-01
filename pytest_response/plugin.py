import py.path
import pytest

from pytest_intercept_remote import remote_status
from pytest_intercept_remote.fixtures import intercept_skip_conditions, intercept_url  # noqa: F401
from pytest_intercept_remote.intercept_helpers import (  # noqa: F401
    intercept_dump,
    intercept_patch,
    intercepted_urls
)

mpatch = pytest.MonkeyPatch()


def pytest_addoption(parser):
    """
    Pytest hook for adding cmd-line options.
    """
    DEFAULT_DUMP_FILE = ".intercepted"

    parser.addoption(
        "--intercept-remote", dest="intercept_remote", action="store_true", default=False,
        help="Intercepts outgoing connections requests.")
    parser.addoption(
        "--remote-status", dest="remote_status", action="store", nargs="?", const="show", default="no",
        help="Reports the status of intercepted urls (show/only/no).")
    parser.addini(
        "intercept_dump_file", "filepath at which intercepted requests are dumped",
        type="string", default=DEFAULT_DUMP_FILE)


def pytest_configure(config):
    """
    Pytest hook for setting up monkeypatch, if ``--intercept-remote`` is ``True``
    """
    if not config.option.intercept_remote and config.option.verbose:
        print(f"Intercept outgoing requests: {config.option.intercept_remote}")

    if config.option.remote_status != "no":
        print(f"Report remote status: {config.option.remote_status}")

    if config.option.intercept_remote:
        global mpatch
        intercept_patch(mpatch)


def pytest_unconfigure(config):
    """
    Pytest hook for cleaning up.
    """
    if config.option.intercept_remote:
        global mpatch
        mpatch.undo()
        intercept_dump(config)


def pytest_collection_modifyitems(session, items, config):
    """
    Pytest hook for adding remote status tests from ``remote_status``
    """
    if config.option.remote_status != "no":
        if config.option.remote_status == "only":
            # deselect all other tests if ``--remote-status=only``
            items[:] = []
        report_module = config.hook.pytest_pycollect_makemodule(
            path=py.path.local(remote_status.__file__),
            parent=session)
        _remote_test_functions = [
            remote_status.test_urls_urllib,
            remote_status.test_urls_requests,
            remote_status.test_urls_socket
        ]

        remote_tests = []
        for testfunc in _remote_test_functions:
            remote_tests.extend(
                config.hook.pytest_pycollect_makeitem(
                    collector=report_module,
                    name=testfunc.__name__,
                    obj=testfunc))

        items.extend(remote_tests)
    return
