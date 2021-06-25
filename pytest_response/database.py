import ast
import zlib
from base64 import b64decode, b64encode
from typing import List, Tuple
from datetime import date
from urllib.parse import urljoin, urlparse

from tinydb import TinyDB, where

from pytest_response.exceptions import MalformedUrl


class ResponseDB:
    """
    Basic database class for `pytest_response`

    Parameters
    ----------
    path : `str`
        Path for the database

    Examples
    --------
    >>> db = ResponseDB("db.json")
    """

    today = date.today().strftime("%Y-%m-%d")
    _path = None
    _database = None

    def __init__(self, path: str) -> None:
        self._path = path
        self._database = TinyDB(path)
        return

    def __repr__(self) -> str:
        return f"<database {self._path}>"

    def index(self, index: str = "url") -> List[str]:
        """
        Returns all occurances of the column `index`.

        Parameters
        ----------
        index : `str`
            Defaults to `url`.

        Returns
        -------
        _occurances : `list`
            All occurances of the selected column `index`.
        """
        elements = self._database.all()
        _occurances = []
        for element in elements:
            _occurances.append(element.get(index))
        return _occurances

    def _sanatize_url(self, url: str) -> str:
        """
        Internal method intended to sanatize urls to a common form:
        Expecting:
            from `http://www.python.org:80` -> `http://www.python.org`

        Parameters
        ----------
        url : `str`
            URL to be sanatized.
        """
        try:
            _urlparsed = urlparse(url)
            _url = "://".join([_urlparsed.scheme, _urlparsed.hostname])
            return urljoin(_url, _urlparsed.path).rstrip("/")
        except Exception:
            raise MalformedUrl

    def insert(self, url: str, response: bytes, headers: dict, status: int = 200, **kwargs) -> None:
        """
        Method for dumping url, headers and responses to the database.
        All additonal kwargs are dumped as well.

        Parameters
        ----------
        url : `str`
            URL of the dump.
        response : `bytes`
            Data captured.
        headers : `str`
            Headers captured.
        status : `int`
            Status code of the response.
        **kwargs : `dict`
            Any additional parameter to be dumped.
        """
        kwargs.update({"url": self._sanatize_url(url)})
        kwargs.update({"cache_date": self.today})
        kwargs.update({"status": str(status)})
        kwargs.update({"headers": b64encode(zlib.compress(str(headers).encode("utf-8"))).decode("utf-8")})
        kwargs.update({"response": b64encode(zlib.compress(response)).decode("utf-8")})
        self._database.upsert(kwargs, where("url") == url)
        return

    def get(self, url: str, **kwargs) -> Tuple[int, bytes, dict]:
        """
        Method for getting response and header for a perticular query `url`.
        Currently working by locating `url` only; multi-query to be implemented later.

        Parameters
        ----------
        url : `str`
            URL to be queried.

        Returns
        -------
        status : `int`
            Status code
        data : `bytes`
            Response data.
        headers : `dict`
            Response header.
        """
        query = where("url") == self._sanatize_url(url)  # and where("request") == "req"
        element = self._database.search(query)
        if element:
            status = element[0].get("status", 200)
            headers = element[0].get("headers", "[]")
            res = element[0].get("response")
            return (
                int(status),
                zlib.decompress(b64decode(res.encode("utf-8"))),
                ast.literal_eval(zlib.decompress(b64decode(headers)).decode("utf-8")),
            )
        return 404, b"", {}

    def all(self) -> dict:
        """
        Method to return all records in the database.

        Returns
        -------
        Return list of all elements.
        """
        return self._database.all()

    def truncate(self):
        """
        Method to purge all records in the database.
        """
        return self._database.truncate()

    def close(self) -> None:
        if isinstance(self._database, TinyDB):
            if self._database._opened:
                self._database.close()

    def __del__(self):
        if isinstance(self._database, TinyDB):
            if self._database._opened:
                self._database.close()
        return

    pass
