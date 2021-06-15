from pytest_response import response


def pytest_addoption(parser):
    """
    Pytest hook for adding cmd-line options.
    """
    parser.addoption(
        "--remote",
        dest="remote",
        action="store_true",
        default=False,
        help="Allow outgoing connections requests.",
    )
    parser.addoption(
        "--remote-capture",
        dest="remote_capture",
        action="store_true",
        default=False,
        help="Capture connections requests.",
    )
    parser.addoption(
        "--response",
        dest="response",
        action="store_true",
        default=False,
        help="Mock connections requests.",
    )


def pytest_configure(config):
    """
    Pytest hook for setting up monkeypatch, if ``--intercept-remote`` is ``True``
    """
    if not config.option.remote and config.option.verbose:
        print(f"Remote: {config.option.remote}")

    if config.option.remote_capture and config.option.response:
        assert not config.option.remote_capture and config.option.response  # either capture or mock_remote
    response.setup_database("basedata.json")
    response.register("urllib_quick")
    response.register("requests_quick")

    # if config.option.remote_capture:
    response.capture = config.option.remote_capture
    # if config.option.response:
    response.response = config.option.response
    # if config.option.remote:
    response.remote = config.option.remote
    response.applyall()


# def pytest_runtest_setup(item):


# def pytest_runtest_teardown(item):


def pytest_unconfigure(config):
    """
    Pytest hook for cleaning up.
    """
    response.unapplyall()
    response.unregister()
    # global mpatch
    # if config.option.mock_remote:
    #     response_unpatch(mpatch)
    # if not config.option.remote:
    #     remote_unpatch(mpatch)
    #     remote_dump(config)
