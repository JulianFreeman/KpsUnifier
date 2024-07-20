# coding: utf8
from .Sqlite3Helper import Column, DataType

columns_d = {
    "entry_id": Column("entry_id", DataType.INTEGER, primary_key=True, unique=True),
    "title": Column("title", DataType.BLOB),
    "username": Column("username", DataType.BLOB),
    "password": Column("password", DataType.BLOB),
    "opt": Column("opt", DataType.TEXT),
    "url": Column("url", DataType.BLOB),
    "notes": Column("notes", DataType.BLOB),
    "uuid": Column("uuid", DataType.TEXT, nullable=False),
    "filepath": Column("filepath", DataType.BLOB, nullable=False),
    "path": Column("path", DataType.BLOB),
    "status": Column("status", DataType.TEXT),  # 只有三种状态：keep, transfer, delete
    "deleted": Column("deleted", DataType.INTEGER, has_default=True, default=0),  # 布尔，只有 1 或者 0
}

all_columns = [
    columns_d["entry_id"],
    columns_d["title"],
    columns_d["username"],
    columns_d["password"],
    columns_d["opt"],
    columns_d["url"],
    columns_d["notes"],
    columns_d["uuid"],
    columns_d["filepath"],
    columns_d["path"],
    columns_d["status"],
    columns_d["deleted"],
]

# 插入数据时使用的列
insert_columns = all_columns[1:-2]

# 查询数据时使用的列
query_columns = [
    columns_d["entry_id"],
    columns_d["title"],
    columns_d["username"],
    columns_d["url"],
    columns_d["status"],
]

# 从数据库中读取 UUID 和 文件路径分析相似度
sim_columns = [
    columns_d["uuid"],
    columns_d["filepath"],
]

uuid_col = columns_d["uuid"]
filepath_col = columns_d["filepath"]
entry_id_col = columns_d["entry_id"]
status_col = columns_d["status"]
deleted_col = columns_d["deleted"]
