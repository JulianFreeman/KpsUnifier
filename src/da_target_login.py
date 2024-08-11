# coding: utf8
from pathlib import Path

from PySide6 import QtWidgets, QtCore, QtGui
from pykeepass import PyKeePass
from pykeepass.exceptions import HeaderChecksumError, CredentialsError


class UiDaTargetLogin(object):
    def __init__(self, window: QtWidgets.QWidget):
        window.setWindowTitle("目标文件")
        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        icon_ellipsis = QtGui.QIcon(":/asset/img/ellipsis.svg")
        self.icon_eye = QtGui.QIcon(":/asset/img/eye.svg")
        self.icon_eye_off = QtGui.QIcon(":/asset/img/eye-off.svg")

        self.hly_path = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_path)
        self.lb_path = QtWidgets.QLabel("路径：", window)
        self.lne_path = QtWidgets.QLineEdit(window)
        self.pbn_browse = QtWidgets.QPushButton(icon=icon_ellipsis, parent=window)
        self.hly_path.addWidget(self.lb_path)
        self.hly_path.addWidget(self.lne_path)
        self.hly_path.addWidget(self.pbn_browse)

        self.hly_password = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_password)
        self.lb_password = QtWidgets.QLabel("密码：", window)
        self.lne_password = QtWidgets.QLineEdit(window)
        self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pbn_eye = QtWidgets.QPushButton(icon=self.icon_eye_off, parent=window)
        self.hly_password.addWidget(self.lb_password)
        self.hly_password.addWidget(self.lne_password)
        self.hly_password.addWidget(self.pbn_eye)

        self.hly_bottom = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_bottom)
        self.pbn_ok = QtWidgets.QPushButton("确定", window)
        self.pbn_cancel = QtWidgets.QPushButton("取消", window)
        self.hly_bottom.addStretch(1)
        self.hly_bottom.addWidget(self.pbn_ok)
        self.hly_bottom.addWidget(self.pbn_cancel)

        self.vly_m.addStretch(1)


class DaTargetLogin(QtWidgets.QDialog):
    def __init__(self, config: dict, parent=None):
        super().__init__(parent)
        self.ui = UiDaTargetLogin(self)
        self.tar_kp: PyKeePass | None = None
        self.config = config

        self.ui.pbn_browse.clicked.connect(self.on_pbn_browse_clicked)
        self.ui.pbn_eye.clicked.connect(self.on_pbn_eye_clicked)
        self.ui.pbn_ok.clicked.connect(self.on_pbn_ok_clicked)
        self.ui.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)

    def on_pbn_browse_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择", self.config["last_open_path"],
                                                            filter="KeePass 2 数据库 (*.kdbx);;所有文件 (*)")
        if len(filename) == 0:
            return
        self.ui.lne_path.setText(filename)
        self.config["last_open_path"] = str(Path(filename).parent)

    def on_pbn_eye_clicked(self):
        if self.ui.lne_password.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.ui.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.ui.pbn_eye.setIcon(self.ui.icon_eye)
        else:
            self.ui.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.ui.pbn_eye.setIcon(self.ui.icon_eye_off)

    def sizeHint(self):
        return QtCore.QSize(540, 40)

    def on_pbn_ok_clicked(self):
        try:
            self.tar_kp = PyKeePass(self.ui.lne_path.text(), self.ui.lne_password.text())
        except CredentialsError:
            QtWidgets.QMessageBox.critical(self, "错误", "keepass 密码错误")
            return
        except (FileNotFoundError, HeaderChecksumError):
            QtWidgets.QMessageBox.critical(self, "错误", "文件不存在或不是 keepass 文件")
            return

        self.accept()

    def on_pbn_cancel_clicked(self):
        self.tar_kp = None
        self.reject()
