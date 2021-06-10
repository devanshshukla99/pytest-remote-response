import urllib.request

from pytest_response.controller import controller
from pytest_response import urllib_interest


def test_connection():
    url = "https://www.python.org"
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    controller.capture = True
    urllib_interest.install()
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_2ing():
    url = "http://www.testingmcafeesites.com/testcat_ac.html"
    controller.capture = False
    urllib_interest.install()
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_ing_ssl():
    url = "https://www.python.org"
    urllib_interest.install()
    controller.capture = True
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()


def test_intercept_2ing_ssl():
    url = "https://www.python.org"
    controller.capture = False
    urllib_interest.install()
    res = urllib.request.urlopen(url)
    assert res.status == 200
    assert res.read()
