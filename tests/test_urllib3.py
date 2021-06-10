import requests

from pytest_response.controller import controller
from pytest_response import urllib3_helpers


def test_connection():
    url = "https://www.python.org"
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    controller.capture = True
    urllib3_helpers.install()
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_2ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    controller.capture = False
    urllib3_helpers.install()
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_ing_ssl():
    url = "https://www.python.org"
    controller.capture = True
    urllib3_helpers.install()
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content


def test_intercept_2ing_ssl():
    url = "https://www.python.org"
    controller.capture = False
    urllib3_helpers.install()
    res = requests.get(url)
    assert res.status_code == 200
    assert res.content
