import ast
import zlib
from base64 import b64decode, b64encode
from datetime import date
from urllib.parse import urlparse, urljoin

from tinydb import TinyDB, where

# from collections.abc import MutableMapping


class ResponseDB:
    today = date.today().strftime("%Y-%m-%d")
    _path = None

    def __init__(self, path) -> None:
        self._path = path
        self._database = TinyDB(path)
        return

    def __repr__(self) -> str:
        return f"<database {self._path}>"

    def index(self, index: str = "url"):
        """
        Returns all occurances of the column `index`. Defaults to "urls".
        """
        elements = self._database.all()
        _occurances = []
        for element in elements:
            _occurances.append(element.get(index))
        return _occurances

    def _sanatize_url(self, url: str):
        """
        Method intended to sanatize urls to a common form:
        Expecting:
            from `http://www.python.org:80` -> `http://www.python.org`
        """
        _urlparsed = urlparse(url)
        _url = "://".join([_urlparsed.scheme, _urlparsed.hostname])
        return urljoin(_url, _urlparsed.path)

    def insert(self, url: str, response: bytes, headers: dict, **kwargs):
        """
        Method for dumping url, headers and responses to the database.
        All additonal kwargs are dumped as well.
        """
        kwargs.update({"url": self._sanatize_url(url)})
        kwargs.update({"cache_date": self.today})
        kwargs.update({"response": b64encode(zlib.compress(response)).decode("utf-8")})
        kwargs.update({"headers": b64encode(zlib.compress(str(headers).encode("utf-8"))).decode("utf-8")})
        self._database.upsert(kwargs, where("url") == url)
        return

    def get(self, url: str, **kwargs):
        """
        Method for getting response and header for a perticular query `url`.
        Currently working by locating `url` only; multi-query to be implemented later.
        """
        query = where("url") == self._sanatize_url(url)  # and where("request") == "req"
        if element := self._database.search(query):
            res = element[0].get("response")
            headers = element[0].get("headers", "[]")
            return zlib.decompress(b64decode(res.encode("utf-8"))), ast.literal_eval(
                zlib.decompress(b64decode(headers)).decode("utf-8")
            )
        return b"", {}

    def all(self):
        """
        Method to return all records in the database.
        """
        return self._database.all()

    def truncate(self):
        """
        Method to purge all records in the database.
        """
        return self._database.truncate()

    def close(self):
        if hasattr(self, "_database"):
            self._database.close()

    def __del__(self):
        if hasattr(self, "_database"):
            self._database.close()
        return

    pass


# class MockHeaders(MutableMapping):
#     def __init__(self, default_headers={""}, *args, **kwargs):
#         self.store = dict()
#         self.update(dict(*args, **kwargs))

#     def __repr__(self):
#         return str(self.store)

#     def __getitem__(self, key):
#         return self.store[key]

#     def __setitem__(self, key, value):
#         self.store[key] = value

#     def __delitem__(self, key):
#         del self.store[key]

#     def __iter__(self):
#         return iter(self.store)

#     def __len__(self):
#         return len(self.store)

#     pass
