# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui
from pykeepass import PyKeePass

from .page_load import PageLoad
from .page_query import PageQuery
from .page_similar import PageSimilar

from .cmbx_styles import StyleComboBox
from lib.Sqlite3Helper import Sqlite3Worker
from lib.db_columns_def import all_columns
from lib.sec_db_columns_def import sec_all_columns
from lib.config_utils import write_config


class UiKpsUnifier(object):
    def __init__(
            self,
            default_db_path: str,
            config: dict,
            file_kp: dict[str, PyKeePass],
            sqh: Sqlite3Worker,
            sec_sqh: Sqlite3Worker,
            window: QtWidgets.QMainWindow
    ):
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
        self.act_similar = QtGui.QAction("相似度", self.cw)
        self.menu_view.addActions([self.act_load, self.act_query, self.act_similar])

        self.menu_help = self.menu_bar.addMenu("帮助")
        self.act_about = QtGui.QAction("关于", self.cw)
        self.act_about_qt = QtGui.QAction("关于 Qt", self.cw)
        self.menu_help.addActions([self.act_about, self.act_about_qt])

        self.hly_top = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_top)

        self.lne_db_path = QtWidgets.QLineEdit(self.cw)
        self.lne_db_path.setEnabled(False)
        self.lne_db_path.setPlaceholderText(default_db_path)
        self.cmbx_styles = StyleComboBox(self.cw)
        self.cmbx_styles.setMinimumWidth(110)
        self.hly_top.addWidget(self.lne_db_path)
        self.hly_top.addWidget(self.cmbx_styles)

        self.sw_m = QtWidgets.QStackedWidget(self.cw)
        self.vly_m.addWidget(self.sw_m)

        self.page_load = PageLoad(config, file_kp, sqh, sec_sqh, self.cw)
        self.sw_m.addWidget(self.page_load)
        self.page_query = PageQuery(config, file_kp, sqh, sec_sqh, self.cw)
        self.sw_m.addWidget(self.page_query)
        self.page_similar = PageSimilar(sqh, config, self.cw)
        self.sw_m.addWidget(self.page_similar)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.page_load.update_sqh(sqh)
        self.page_query.update_sqh(sqh)


class KpsUnifier(QtWidgets.QMainWindow):
    def __init__(
            self,
            db_path: str,
            secrets_path: str,
            config: dict,
            version: str,
            parent: QtWidgets.QWidget = None,
    ):
        super().__init__(parent)
        self.db_path = db_path
        self.secrets_path = secrets_path
        self.config = config
        self.version = version
        self.file_kp: dict[str, PyKeePass] = {}
        self.sqh = self.init_db()
        self.sec_sqh = self.init_secrets_db()

        self.ui = UiKpsUnifier(self.db_path, self.config, self.file_kp, self.sqh, self.sec_sqh, self)

        self.ui.act_new.triggered.connect(self.on_act_new_triggered)
        self.ui.act_open.triggered.connect(self.on_act_open_triggered)
        self.ui.act_load.triggered.connect(self.on_act_load_triggered)
        self.ui.act_query.triggered.connect(self.on_act_query_triggered)
        self.ui.act_similar.triggered.connect(self.on_act_similar_triggered)

        self.ui.act_about.triggered.connect(self.on_act_about_triggered)
        self.ui.act_about_qt.triggered.connect(self.on_act_about_qt_triggered)

    def __del__(self):
        self.config["last_db_path"] = self.db_path
        write_config(self.config,
                     QtWidgets.QApplication.organizationName(),
                     QtWidgets.QApplication.applicationName())

    def sizeHint(self):
        return QtCore.QSize(860, 640)

    def init_db(self) -> Sqlite3Worker:
        sqh = Sqlite3Worker(self.db_path)
        sqh.create_table(self.config["table_name"], all_columns, if_not_exists=True)
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

    def on_act_similar_triggered(self):
        self.ui.sw_m.setCurrentIndex(2)

    def on_act_about_triggered(self):
        QtWidgets.QMessageBox.about(
            self,
            "关于",
            f"一个可以同时处理多个 keepass 文件的工具。\n\n版本：v{self.version}"
        )

    def on_act_about_qt_triggered(self):
        QtWidgets.QMessageBox.aboutQt(self, "关于 Qt")

    def init_secrets_db(self) -> Sqlite3Worker:
        sec_sqh = Sqlite3Worker(self.secrets_path)
        sec_sqh.create_table("secrets", sec_all_columns, if_not_exists=True)
        return sec_sqh
