from flask import g
import sqlite3


def get_db_conn() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect("rss.db")
        g.db.row_factory = dict_factory
    return g.db


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}
