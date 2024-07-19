# coding: utf8
from pathlib import Path
from PySide6 import QtWidgets, QtGui, QtCore
from pykeepass.exceptions import CredentialsError

from lib.Sqlite3Helper import Sqlite3Worker
from lib.kps_operations import read_kps_to_db


class GbxKpsLogin(QtWidgets.QGroupBox):
    def __init__(
            self,
            path: str,
            sqh: Sqlite3Worker,
            config: dict,
            parent: QtWidgets.QWidget = None
    ):
        super().__init__(parent)
        self.sqh = sqh
        self.config = config
        self.path = path

        self.icon_eye = QtGui.QIcon(":/asset/img/eye.svg")
        self.icon_eye_off = QtGui.QIcon(":/asset/img/eye-off.svg")

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        self.hly_path = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_path)

        self.lb_path = QtWidgets.QLabel("路径：", self)
        self.hly_path.addWidget(self.lb_path)
        self.lne_path = QtWidgets.QLineEdit(path, self)
        self.lne_path.setEnabled(False)
        self.hly_path.addWidget(self.lne_path)

        self.hly_password = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_password)

        self.lb_password = QtWidgets.QLabel("密码：", self)
        self.hly_password.addWidget(self.lb_password)
        self.lne_password = QtWidgets.QLineEdit(self)
        self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.hly_password.addWidget(self.lne_password)

        self.pbn_eye = QtWidgets.QPushButton(icon=self.icon_eye_off, parent=self)
        self.hly_password.addWidget(self.pbn_eye)

        self.hly_bottom = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_bottom)
        self.lb_loaded = QtWidgets.QLabel("【已加载】", self)
        self.hly_bottom.addWidget(self.lb_loaded)
        self.lb_loaded.setVisible(False)
        self.hly_bottom.addStretch(1)

        self.pbn_load = QtWidgets.QPushButton("加载", self)
        self.hly_bottom.addWidget(self.pbn_load)
        self.pbn_remove = PushButtonWithItem(self, self, "移除")
        self.hly_bottom.addWidget(self.pbn_remove)

        self.pbn_eye.clicked.connect(self.on_pbn_eye_clicked)
        self.pbn_load.clicked.connect(self.on_pbn_load_clicked)
        # 回车加载
        self.lne_password.returnPressed.connect(self.on_pbn_load_clicked)

    def set_loaded(self, loaded: bool):
        self.lb_loaded.setVisible(loaded)
        self.pbn_load.setDisabled(loaded)
        # 防止回车键触发加载
        self.lne_password.setDisabled(loaded)

    def on_pbn_eye_clicked(self):
        is_pass_mode = self.lne_password.echoMode() == QtWidgets.QLineEdit.EchoMode.Password
        if is_pass_mode:
            self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.pbn_eye.setIcon(self.icon_eye)
        else:
            self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.pbn_eye.setIcon(self.icon_eye_off)

    def on_pbn_load_clicked(self):
        try:
            read_kps_to_db(
                kps_file=self.lne_path.text(),
                password=self.lne_password.text(),
                table_name=self.config["table_name"],
                sqh=self.sqh
            )
        except CredentialsError:
            QtWidgets.QMessageBox.critical(self, "密码错误",
                                           f"{self.lne_path.text()}\n密码错误")
            return

        self.lne_password.clear()
        self.set_loaded(True)
        loaded_mem = self.config["loaded_memory"]
        db_name = Path(self.sqh.db_name).name
        if db_name not in loaded_mem:
            loaded_mem[db_name] = []
        loaded_mem[db_name].append(self.lne_path.text())


class PushButtonWithItem(QtWidgets.QPushButton):

    clicked_with_item = QtCore.Signal(GbxKpsLogin)

    def __init__(self, item: GbxKpsLogin, parent: QtWidgets.QWidget = None, title: str = ""):
        super().__init__(title, parent)
        self.item = item
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_item.emit(self.item)
