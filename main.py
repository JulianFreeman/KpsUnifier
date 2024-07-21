# coding: utf8
import sys

from PySide6.QtWidgets import QApplication

from lib.config_utils import (
    get_default_db_path,
    read_config,
    get_secrets_path,
    write_config,
)
from src.mw_kps_unifier import KpsUnifier
import src.rc_kps_unifier

__version__ = '1.1.1'
__version_info__ = tuple(map(int, __version__.split('.')))

ORG_NAME = "JnPrograms"
APP_NAME = "KpsUnifier"


def main():
    app = QApplication(sys.argv)
    app.setOrganizationName(ORG_NAME)
    app.setApplicationName(APP_NAME)

    config = read_config(ORG_NAME, APP_NAME)
    db_path = get_default_db_path(config, ORG_NAME, APP_NAME)
    secrets_path = get_secrets_path(ORG_NAME, APP_NAME)

    win = KpsUnifier(db_path, secrets_path, config,
                     ORG_NAME, APP_NAME, __version__)
    win.show()
    app.exec()

    config["last_db_path"] = win.db_path
    write_config(config, ORG_NAME, APP_NAME)


if __name__ == '__main__':
    main()
