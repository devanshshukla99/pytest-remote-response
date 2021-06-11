import pytest
import urllib.request

from pytest_response import response

# @pytest.fixture(scope="module", autouse=True)
# def apply_interceptor():
#     pr_app = app()
#     pr_app.register("urllib")
#     pr_app.apply()
#     yield
#     pr_app.unregister()
#     return


def test_connection():
    url = "https://www.python.org"
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    # response.capture = True
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_2ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    # response.capture = False
    # response.response = True
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_ing_ssl():
    url = "https://www.python.org"
    # response.capture = True
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_2ing_ssl():
    url = "https://www.python.org"
    # response.capture = False
    # response.response = True
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()
