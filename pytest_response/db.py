from datetime import date
from tinydb import TinyDB, where

DEFAULT_DB = "./db.json"
TODAY = date.today().strftime("%Y-%m-%d")
db = TinyDB(DEFAULT_DB)


def insert(url, db_dict):
    global TODAY, db
    db_dict.update({"cache_date": TODAY})

    db.upsert(
        db_dict,
        where("url") == url)
    return


def get(url, **kwargs):
    global TODAY, db
    query = where("url") == url  # and where("request") == "req"
    if element := db.search(query):
        # print(element)
        res = element[0]["response"]
        return res


def all():
    global TODAY, db
    return db.all()
