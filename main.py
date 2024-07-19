# coding: utf8
import sys

from PySide6.QtWidgets import QApplication

from src.mw_kps_unifier import KpsUnifier
import src.rc_kps_unifier


def main():
    app = QApplication(sys.argv)
    win = KpsUnifier()
    win.show()
    return app.exec()


if __name__ == '__main__':
    main()
