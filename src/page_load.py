# coding: utf8
from PySide6 import QtWidgets
from pykeepass.exceptions import CredentialsError

from .gbx_kps_login import GbxKpsLogin
from lib.Sqlite3Helper import Sqlite3Worker
from lib.db_columns_def import all_columns
from lib.kps_operations import read_kps_to_db


class WgLoadKps(QtWidgets.QWidget):
    def __init__(self, sqh: Sqlite3Worker, parent=None):
        super().__init__(parent)
        self.sqh = sqh
        self.kps_wgs: list[GbxKpsLogin] = []

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)
        self.vly_m.addStretch(1)

    def add_kps(self, path: str):
        wg = GbxKpsLogin(path, self)
        wg.pbn_remove.clicked_with_item.connect(self.on_item_pbn_remove_clicked)
        wg.pbn_load.clicked_with_item.connect(self.on_item_pbn_load_clicked)
        # 从倒数第二个位置插入，保证弹簧始终在最后
        self.vly_m.insertWidget(self.vly_m.count() - 1, wg)
        self.kps_wgs.append(wg)

    def on_item_pbn_remove_clicked(self, item: GbxKpsLogin):
        self.vly_m.removeWidget(item)
        item.deleteLater()

    def on_item_pbn_load_clicked(self, item: GbxKpsLogin):
        try:
            read_kps_to_db(kps_file=item.lne_path.text(),
                           password=item.lne_password.text(),
                           columns=all_columns[1:],
                           sqh=self.sqh)
        except CredentialsError:
            QtWidgets.QMessageBox.critical(self, "密码错误",
                                           f"{item.lne_path.text()}\n密码错误")
            return

        item.set_loaded(True)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.sqh = sqh
        for wg in self.kps_wgs:
            wg.set_loaded(False)


class PageLoad(QtWidgets.QWidget):
    def __init__(self, sqh: Sqlite3Worker, parent=None):
        super().__init__(parent)
        self.hly_m = QtWidgets.QHBoxLayout()
        self.setLayout(self.hly_m)
        self.vly_left = QtWidgets.QVBoxLayout()
        self.hly_m.addLayout(self.vly_left)

        self.pbn_add = QtWidgets.QPushButton("添加", self)
        self.vly_left.addWidget(self.pbn_add)
        self.pbn_load_all = QtWidgets.QPushButton("加载全部", self)
        self.vly_left.addWidget(self.pbn_load_all)
        self.vly_left.addStretch(1)

        self.sa = QtWidgets.QScrollArea(self)
        self.sa.setWidgetResizable(True)
        self.hly_m.addWidget(self.sa)
        self.wg_sa = WgLoadKps(sqh, self.sa)
        self.sa.setWidget(self.wg_sa)

        self.hly_m.setStretchFactor(self.vly_left, 1)
        self.hly_m.setStretchFactor(self.sa, 6)

        self.pbn_add.clicked.connect(self.on_pbn_add_clicked)

    def on_pbn_add_clicked(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "选择", "../",
                                                              filter="KeePass 2 数据库 (*.kdbx);;所有文件 (*)")
        if len(filenames) == 0:
            return
        for filename in filenames:
            self.wg_sa.add_kps(filename)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.wg_sa.update_sqh(sqh)
