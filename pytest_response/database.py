import ast
import zlib
import sqlite3
from base64 import b64decode, b64encode
from typing import List, Tuple
from datetime import date
from urllib.parse import urljoin, urlparse

from pytest_response.exceptions import MalformedUrl

__all__ = ["ResponseDB"]

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

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
        self._database = sqlite3.connect(path)
        self.setup()
        return

    def __repr__(self) -> str:
        return f"<database {self._path}>"
    
    def setup(self) -> bool:
        self._database.cursor().executescript("""
            CREATE TABLE IF NOT EXISTS records (
            url TEXT PRIMARY KEY NOT NULL,
            cache_date DATE NOT NULL,
            status TEXT NOT NULL,
            headers TEXT NOT NULL,
            response TEXT NOT NULL
        );
        """)
        self._database.commit()
        self._database.row_factory = dict_factory
        return True

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
        elements = self._database.execute("SELECT * FROM records;").fetchall()
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

        _kwargs = [b64encode(self._sanatize_url(url).encode()).decode(), self.today, str(status), b64encode(zlib.compress(str(headers).encode("utf-8"))).decode("utf-8"), b64encode(zlib.compress(response)).decode("utf-8")]
        self._database.execute("REPLACE INTO records(url, cache_date, status, headers, response) VALUES (?,?,?,?,?)", _kwargs)
        self._database.commit()
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
        # query = where("url") == self._sanatize_url(url)  # and where("request") == "req"
        # element = self._database.search(query)
        url = b64encode(self._sanatize_url(url).encode()).decode()
        element = self._database.execute(f"SELECT * FROM records WHERE url='{url}';").fetchall()
        if element:
            status = element[-1].get("status", 200)
            headers = element[-1].get("headers", "[]")
            res = element[-1].get("response")
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
        return self._database.execute("SELECT * FROM records").fetchall()

    def truncate(self):
        """
        Method to purge all records in the database.
        """
        self._database.execute("DELETE FROM records;")
        return self._database.commit()

    def close(self) -> None:
        self._database.close()

        # if isinstance(self._database, TinyDB):
        #     if self._database._opened:
        #         self._database.close()

    def __del__(self):
        self._database.close()
        # if isinstance(self._database, TinyDB):
        #     if self._database._opened:
        #         self._database.close()
        return

    pass
