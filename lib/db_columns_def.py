# coding: utf8
from .Sqlite3Helper import Column, DataType

columns_d = {
    "entry_id": Column("entry_id", DataType.INTEGER, primary_key=True),
    "title": Column("title", DataType.BLOB),
    "username": Column("username", DataType.BLOB),
    "password": Column("password", DataType.BLOB),
    "opt": Column("opt", DataType.TEXT),
    "url": Column("url", DataType.BLOB),
    "notes": Column("notes", DataType.BLOB),
    "path": Column("path", DataType.BLOB, nullable=False),
}

all_columns = [
    columns_d["entry_id"],
    columns_d["title"],
    columns_d["username"],
    columns_d["password"],
    columns_d["opt"],
    columns_d["url"],
    columns_d["notes"],
    columns_d["path"],
]

query_columns = [
    columns_d["entry_id"],
    columns_d["title"],
    columns_d["username"],
    columns_d["url"],
]
