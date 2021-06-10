from pytest_response.interceptors import urllib3
import requests
import pytest
from pytest_response.app import control, app


@pytest.fixture(scope="function")
def apply_interceptor():
    pr_app = app()
    pr_app.register("urllib3")
    pr_app.apply()
    return


@pytest.mark.usefixtures("apply_interceptor")
def test_connection():
    url = "https://www.python.org"
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


@pytest.mark.usefixtures("apply_interceptor")
def test_intercept_ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    control.capture = True
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


@pytest.mark.usefixtures("apply_interceptor")
def test_intercept_2ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    control.capture = False
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


@pytest.mark.usefixtures("apply_interceptor")
def test_intercept_ing_ssl():
    url = "https://www.python.org"
    control.capture = True
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


@pytest.mark.usefixtures("apply_interceptor")
def test_intercept_2ing_ssl():
    url = "https://www.python.org"
    control.capture = False
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content
