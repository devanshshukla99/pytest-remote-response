# Mock outgoing connections for `urllib3` library

import urllib3

from pytest_response import response

# Setup the database file
response.setup_database("basedata.json")

# Capture outgoing connections
response.configure(remote=True, capture=False, response=True)

# Applies the `urllib3` interceptor
response.post("urllib3")

http = urllib3.PoolManager()
url = "https://www.python.org"

# Since the interceptors are in response mode, the response data and headers
# will be spoofed with saved data in the database;
# if the query comes back empty, this request will
# error out with :class:`pytest_response.exceptions.ResponseNotFound`
res = http.request("GET", url)

# Cleanup
response.unpost()
