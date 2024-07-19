# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui
from .page_load import PageLoad
from .cmbx_styles import StyleComboBox


class UiKpsUnifier(object):
    def __init__(self, window: QtWidgets.QMainWindow):
        window.setWindowTitle('KeePassXC 多合一')
        self.cw = QtWidgets.QWidget(window)
        self.vly_m = QtWidgets.QVBoxLayout()
        self.cw.setLayout(self.vly_m)
        window.setCentralWidget(self.cw)

        self.menu_bar = window.menuBar()
        self.menu_file = self.menu_bar.addMenu("文件")
        self.act_new = QtGui.QAction("新建", self.cw)
        self.act_open = QtGui.QAction("打开", self.cw)
        self.menu_file.addActions([self.act_new, self.act_open])

        self.menu_view = self.menu_bar.addMenu("视图")
        self.act_load = QtGui.QAction("加载", self.cw)
        self.act_query = QtGui.QAction("查询", self.cw)
        self.menu_view.addActions([self.act_load, self.act_query])

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lne_db_path = QtWidgets.QLineEdit(self.cw)
        self.lne_db_path.setEnabled(False)
        self.cmbx_styles = StyleComboBox(self.cw)
        self.hly_top.addWidget(self.lne_db_path)
        self.hly_top.addWidget(self.cmbx_styles)

        self.sw_m = QtWidgets.QStackedWidget(self.cw)
        self.vly_m.addWidget(self.sw_m)

        self.page_load = PageLoad(self.cw)
        self.sw_m.addWidget(self.page_load)
        self.page_query = QtWidgets.QWidget(self.cw)
        self.sw_m.addWidget(self.page_query)


class KpsUnifier(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = UiKpsUnifier(self)

        self.ui.act_open.triggered.connect(self.on_act_open_triggered)
        self.ui.act_load.triggered.connect(self.on_act_load_triggered)
        self.ui.act_query.triggered.connect(self.on_act_query_triggered)

    def sizeHint(self):
        return QtCore.QSize(860, 640)

    def on_act_open_triggered(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开", "../")
        if len(filename) == 0:
            return
        self.ui.lne_db_path.setText(filename)

    def on_act_load_triggered(self):
        self.ui.sw_m.setCurrentIndex(0)

    def on_act_query_triggered(self):
        self.ui.sw_m.setCurrentIndex(1)
