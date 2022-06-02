# Import the database interface :class:`pytest_response.database.ResponseDB`
from pytest_response.database import ResponseDB

# Setup the database
db = ResponseDB(path="database.json")

# Insert new element
url = "https://www.python.org"
status = 200
headers = {}
data = b""
db.insert(url=url, status=status, response=data, headers=headers)

# Verify the index
assert url in db.index()

# Query for an URL
url = "https://www.python.org"
get_status, get_data, get_headers = db.get(url)

# Verify the data is unchanged
assert status == get_status
assert data == get_data
assert headers == get_headers
