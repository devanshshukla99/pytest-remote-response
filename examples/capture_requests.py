# Capture outgoing connections for `requests` library

from pytest_response import response

# Setting up a clean database
response.setup_database("database.json")

# Capture outgoing connections
response.configure(remote=True, capture=True, response=False)

# Applies the `requests` interceptor
response.post("requests")

# It's important to import the function after setting up `response`,
# to make sure the monkey patched version is used
import requests  # noqa

# Since the interceptors are in capture mode, the response data and headers
# will be dumped in the database file, i.e. database.json
r = requests.get("https://www.python.org")

# Cleanup
response.unpost()
