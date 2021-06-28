# Capture outgoing connections for `requests` library

import requests
from pytest_response import response

# Setup the database file
response.setup_database("basedata.json")

# Capture outgoing connections
response.configure(remote=True, capture=True, response=False)

# Applies the `requests` interceptor
response.post("requests")

# Since the interceptors are in capture mode, the response data and headers
# will be dumped in the database file, i.e. basedata.json
r = requests.get("https://www.python.org")

# Cleanup
response.unpost()
