# coding: utf8
import os
import sys
from datetime import datetime
from pathlib import Path
from PySide6 import QtWidgets, QtCore, QtGui

from .page_load import PageLoad
from .cmbx_styles import StyleComboBox
from lib.Sqlite3Helper import Sqlite3Worker
from lib.db_columns_def import all_columns


def get_default_db_path() -> str:
    plat = sys.platform
    if plat == "win32":
        data_dir = os.path.expandvars("%appdata%")
    elif plat == "darwin":
        data_dir = os.path.expanduser("~/Library/Application Support")
    else:
        raise OSError("Unsupported platform")
    app_dir = Path(data_dir,
                   QtWidgets.QApplication.organizationName(),
                   QtWidgets.QApplication.applicationName())
    if not app_dir.exists():
        app_dir.mkdir(parents=True, exist_ok=True)

    now_s = datetime.now().strftime("%Y%m%d%H%M%S")
    return str(app_dir / f"{now_s}.db")


class UiKpsUnifier(object):
    def __init__(self, default_db_path: str, sqh: Sqlite3Worker, window: QtWidgets.QMainWindow):
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
        self.lne_db_path.setPlaceholderText(default_db_path)
        self.cmbx_styles = StyleComboBox(self.cw)
        self.hly_top.addWidget(self.lne_db_path)
        self.hly_top.addWidget(self.cmbx_styles)

        self.sw_m = QtWidgets.QStackedWidget(self.cw)
        self.vly_m.addWidget(self.sw_m)

        self.page_load = PageLoad(sqh, self.cw)
        self.sw_m.addWidget(self.page_load)
        self.page_query = QtWidgets.QWidget(self.cw)
        self.sw_m.addWidget(self.page_query)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.page_load.update_sqh(sqh)


class KpsUnifier(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db_path = get_default_db_path()
        self.sqh = self.init_db()

        self.ui = UiKpsUnifier(self.db_path, self.sqh, self)

        self.ui.act_new.triggered.connect(self.on_act_new_triggered)
        self.ui.act_open.triggered.connect(self.on_act_open_triggered)
        self.ui.act_load.triggered.connect(self.on_act_load_triggered)
        self.ui.act_query.triggered.connect(self.on_act_query_triggered)

    def sizeHint(self):
        return QtCore.QSize(860, 640)

    def init_db(self) -> Sqlite3Worker:
        sqh = Sqlite3Worker(self.db_path)
        sqh.create_table("entries", all_columns, if_not_exists=True)
        return sqh

    def update_db(self, filename: str):
        self.db_path = filename
        self.sqh = self.init_db()
        self.ui.update_sqh(self.sqh)
        self.ui.lne_db_path.setText(filename)

    def on_act_new_triggered(self):
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "新建", "../",
                                                            filter="数据库 (*.db);;所有文件 (*)")
        if len(filename) == 0:
            return
        self.update_db(filename)

    def on_act_open_triggered(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开", "../",
                                                            filter="数据库 (*.db);;所有文件 (*)")
        if len(filename) == 0:
            return
        self.update_db(filename)

    def on_act_load_triggered(self):
        self.ui.sw_m.setCurrentIndex(0)

    def on_act_query_triggered(self):
        self.ui.sw_m.setCurrentIndex(1)
