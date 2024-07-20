# coding: utf8
from os import PathLike
from pykeepass import PyKeePass
from lib.db_columns_def import insert_columns
from .Sqlite3Helper import Sqlite3Worker, BlobType


def trim_str(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return value


def extract_otp(otp: str) -> str:
    if otp is None:
        return ""
    params = otp.split("?", 1)[1]
    secret = params.split("&")[0]
    return secret.split("=")[1]


def blob_fy(value: str) -> BlobType:
    if value is None:
        return BlobType()
    return BlobType(value.encode("utf-8"))


def read_kps_to_db(kps_file: str | PathLike[str], password: str,
                   table_name: str, sqh: Sqlite3Worker) -> PyKeePass:
    kp = PyKeePass(kps_file, password=password)

    values = []
    for group in kp.groups:
        for entry in group.entries:
            values.append([
                blob_fy(trim_str(entry.title)),
                blob_fy(trim_str(entry.username)),
                blob_fy(entry.password),
                blob_fy(extract_otp(entry.otp)),
                blob_fy(trim_str(entry.url)),
                blob_fy(entry.notes),
                str(entry.uuid),
                blob_fy(kps_file),
                blob_fy("::".join(entry.path[:-1])),
            ])

    sqh.insert_into(table_name, insert_columns, values)
    return kp
