import ast
from datetime import date
from base64 import b64encode, b64decode
from tinydb import TinyDB, where
import zlib

DEFAULT_DB = "./db.json"
TODAY = date.today().strftime("%Y-%m-%d")


class _db:
    def __init__(self):
        global DEFAULT_DB, TODAY
        self.db = TinyDB(DEFAULT_DB)
        self.today = TODAY

    def index(self, index):
        elements = self.db.all()
        _occurances = []
        for element in elements:
            _occurances.append(element.get(index))
        return _occurances

    def insert(self, url, response, **kwargs):
        kwargs.update({"url": url})
        kwargs.update({"cache_date": self.today})
        kwargs.update({"response": b64encode(zlib.compress(response)).decode("utf-8")})
        self.db.upsert(kwargs, where("url") == url)
        return

    def get(self, url, **kwargs):
        query = where("url") == url  # and where("request") == "req"
        if element := self.db.search(query):
            res = element[0].get("response")
            headers = element[0].get("headers", "[]")
            return zlib.decompress(b64decode(res.encode("utf-8"))), dict.fromkeys(
                ast.literal_eval(headers)
            )
        return b"", {}

    def all(self):
        return self.db.all()

    def __del__(self):
        self.db.close()
        return

    pass


db = _db()
