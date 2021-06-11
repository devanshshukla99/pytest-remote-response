import requests
import pytest

from pytest_response import response


# @pytest.fixture(scope="function")
# def apply_interceptor():
#     pr_app = app()
#     pr_app.register("urllib3")
#     pr_app.apply()
#     return


def test_connection():
    url = "https://www.python.org"
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    # response.capture = True
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_2ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    # response.capture = False
    # response.response = True
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_ing_ssl():
    url = "https://www.python.org"
    # response.capture = True
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_2ing_ssl():
    url = "https://www.python.org"
    # response.capture = False
    # response.response = True
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content
