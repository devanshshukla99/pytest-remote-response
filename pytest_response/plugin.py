import py.path
import pytest

from pytest_response import remote_status
from pytest_response.fixtures import (
    intercept_skip_conditions,
    intercept_url,
)  # noqa: F401
from pytest_response.remote_helpers import (  # noqa: F401
    remote_dump,
    remote_patch,
    remote_unpatch,
    intercepted_urls,
)
from pytest_response.respond import response_patch, response_unpatch  # noqa: F401

# from gevent import monkey

mpatch = pytest.MonkeyPatch()


def pytest_addoption(parser):
    """
    Pytest hook for adding cmd-line options.
    """
    DEFAULT_DUMP_FILE = ".intercepted"

    parser.addoption(
        "--remote",
        dest="remote",
        action="store_true",
        default=False,
        help="Intercepts outgoing connections requests.",
    )
    parser.addoption(
        "--mock-remote",
        dest="mock_remote",
        action="store_true",
        default=False,
        help="Intercepts outgoing connections requests.",
    )
    # parser.addoption(
    #     "--remote-status",
    #     dest="remote_status",
    #     action="store",
    #     nargs="?",
    #     const="show",
    #     default="no",
    #     help="Reports the status of intercepted urls (show/only/no).",
    # )
    # parser.addini(
    #     "intercept_dump_file",
    #     "filepath at which intercepted requests are dumped",
    #     type="string",
    #     default=DEFAULT_DUMP_FILE,
    # )


def pytest_configure(config):
    """
    Pytest hook for setting up monkeypatch, if ``--intercept-remote`` is ``True``
    """
    global mpatch

    if not config.option.remote and config.option.verbose:
        print(f"Remote: {config.option.remote}")

    # if config.option.remote_status != "no":
    #     print(f"Report remote status: {config.option.remote_status}")

    if config.option.mock_remote:
        response_patch(mpatch)
    elif not config.option.remote:
        remote_patch(mpatch)


def pytest_unconfigure(config):
    """
    Pytest hook for cleaning up.
    """
    global mpatch
    if config.option.mock_remote:
        response_unpatch(mpatch)
    if not config.option.remote:
        remote_unpatch(mpatch)
        remote_dump(config)


# def pytest_collection_modifyitems(session, items, config):
#     """
#     Pytest hook for adding remote status tests from ``remote_status``
#     """
#     if config.option.remote_status != "no":
#         if config.option.remote_status == "only":
#             # deselect all other tests if ``--remote-status=only``
#             items[:] = []
#         report_module = config.hook.pytest_pycollect_makemodule(
#             path=py.path.local(remote_status.__file__), parent=session
#         )
#         _remote_test_functions = [
#             remote_status.test_urls_urllib,
#             remote_status.test_urls_requests,
#             remote_status.test_urls_socket,
#         ]

#         remote_tests = []
#         for testfunc in _remote_test_functions:
#             remote_tests.extend(
#                 config.hook.pytest_pycollect_makeitem(
#                     collector=report_module, name=testfunc.__name__, obj=testfunc
#                 )
#             )

#         items.extend(remote_tests)
#     return
