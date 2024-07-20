# coding: utf8
from .Sqlite3Helper import Column, DataType

sec_columns_d = {
    "secret_id": Column("secret_id", DataType.INTEGER, primary_key=True, unique=True),
    "filepath": Column("filepath", DataType.BLOB),
    "password": Column("password", DataType.BLOB),
}

sec_all_columns = [
    sec_columns_d["secret_id"],
    sec_columns_d["filepath"],
    sec_columns_d["password"],
]

insert_sec_columns = sec_all_columns[1:]

sec_filepath_col = sec_columns_d["filepath"]
sec_password_col = sec_columns_d["password"]
