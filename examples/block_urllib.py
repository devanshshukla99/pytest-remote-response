# Block outgoing connections for `urllib` library

from urllib.request import urlopen
from pytest_response import response

# Setup the database file
response.setup_database("basedata.json")

# Block outgoing connections
response.configure(remote=False, capture=False, response=False)

# Applies the `urllib` interceptor
response.post("urllib")

# Since the connections are blocked, this request will
# error out with :class:`~pytest_response.exceptions.RemoteBlockedError`
r = urlopen("https://www.python.org")

# Cleanup
response.unpost()
