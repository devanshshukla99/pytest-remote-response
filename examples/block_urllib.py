# Block outgoing connections for `urllib` library

from pytest_response import response

# Setting up a clean database
response.setup_database("database.json")

# Block outgoing connections
response.configure(remote=False, capture=False, response=False)

# Applies the `urllib` interceptor
response.post("urllib")

# It's important to import the function after setting up `response`,
# to make sure the monkey patched version is used
from urllib.request import urlopen  # noqa

# Since the connections are blocked, this request will
# error out with :class:`~pytest_response.exceptions.RemoteBlockedError`
r = urlopen("https://www.python.org")

# Cleanup
response.unpost()
