from pytest_response import response


def pytest_addoption(parser):
    """
    Pytest hook for adding cmd-line options.

    Adds relevent cmd-line and ini-config options.
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
        help="Mocks connection requests from database",
    )
    parser.addoption(
        "--remote-database",
        dest="remote_db",
        action="store",
        type=str,
        default="database.json",
        help="Filename to store and mock the connections requests --remote-database=[DUMPFILE]",
    )
    parser.addoption(
        "--remote-block",
        dest="remote_block",
        action="store_false",
        default=True,
        help="Blocks remote connection requests for all interceptors.",
    )


def pytest_configure(config):
    """
    Pytest hook for setting up :class:`pytest_response.app.Response`
    """
    # either remote_capture or remote_response
    if config.option.remote_capture and config.option.remote_response:
        assert not config.option.remote_capture and config.option.remote_response

    # if config.option.init_response:
    response.setup_database(config.option.remote_db)
    response.configure(
        remote=bool(config.option.remote_block),
        capture=bool(config.option.remote_capture),
        response=config.option.remote_response,
    )

def pytest_unconfigure(config):
    """
    Pytest hook for cleaning up.
    """
    if config.option.remote_capture or config.option.remote_response:
        response.unpost()
