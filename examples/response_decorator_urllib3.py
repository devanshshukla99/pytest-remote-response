import urllib3  # noqa
from pytest_response import response

response.configure(remote=True, capture=True, response=False)


@response.activate("urllib3")
def get_url():
    http = urllib3.PoolManager()
    url = "https://www.python.org"

    # Since the interceptors are in response mode, the response data and headers
    # will be spoofed with saved data in the database;
    # if the query comes back empty, this request will
    # error out with :class:`pytest_response.exceptions.ResponseNotFound`
    res = http.request("GET", url)
    assert res.status == 200
    assert res.data


get_url()
