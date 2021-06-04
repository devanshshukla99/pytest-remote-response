import py.path
import pytest

__all__ = ["intercept_url", "intercept_skip_conditions"]


@pytest.fixture
def intercept_url(request):
    if not request.param:
        pytest.skip("got empty parameter set")
    return request.param


@pytest.fixture(scope="function")
def intercept_skip_conditions(request):
    """
    Pytest fixture for enforcing skip conditions.
    """
    if request.config.option.intercept_remote:
        pytest.skip("rerun without --intercept-remote option")

    if not py.path.local(request.config.getini("intercept_dump_file")).isfile():
        pytest.skip("intercept_dump not available")
