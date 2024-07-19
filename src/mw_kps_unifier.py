# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui
from .tab_load import TabLoad


class UiKpsUnifier(object):
    def __init__(self, window: QtWidgets.QWidget):
        window.setWindowTitle('KeePassXC 多合一')
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.tw_m = QtWidgets.QTabWidget(window)
        self.vly_m.addWidget(self.tw_m)

        self.tab_load = TabLoad(window)
        self.tw_m.addTab(self.tab_load, "加载")
        self.tab_query = QtWidgets.QWidget(window)
        self.tw_m.addTab(self.tab_query, "查询")


class KpsUnifier(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiKpsUnifier(self)

    def sizeHint(self):
        return QtCore.QSize(860, 640)
