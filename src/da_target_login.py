# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui


class DaTargetLogin(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("目标文件")
        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)

        icon_ellipsis = QtGui.QIcon(":/asset/img/ellipsis.svg")
        self.icon_eye = QtGui.QIcon(":/asset/img/eye.svg")
        self.icon_eye_off = QtGui.QIcon(":/asset/img/eye-off.svg")

        self.hly_path = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_path)
        self.lb_path = QtWidgets.QLabel("路径：", self)
        self.lne_path = QtWidgets.QLineEdit(self)
        self.pbn_browse = QtWidgets.QPushButton(icon=icon_ellipsis, parent=self)
        self.hly_path.addWidget(self.lb_path)
        self.hly_path.addWidget(self.lne_path)
        self.hly_path.addWidget(self.pbn_browse)

        self.hly_password = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_password)
        self.lb_password = QtWidgets.QLabel("密码：", self)
        self.lne_password = QtWidgets.QLineEdit(self)
        self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.pbn_eye = QtWidgets.QPushButton(icon=self.icon_eye_off, parent=self)
        self.hly_password.addWidget(self.lb_password)
        self.hly_password.addWidget(self.lne_password)
        self.hly_password.addWidget(self.pbn_eye)

        self.hly_bottom = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_bottom)
        self.pbn_ok = QtWidgets.QPushButton("确定", self)
        self.pbn_cancel = QtWidgets.QPushButton("取消", self)
        self.hly_bottom.addStretch(1)
        self.hly_bottom.addWidget(self.pbn_ok)
        self.hly_bottom.addWidget(self.pbn_cancel)

        self.vly_m.addStretch(1)

        self.pbn_browse.clicked.connect(self.on_pbn_browse_clicked)
        self.pbn_eye.clicked.connect(self.on_pbn_eye_clicked)
        self.pbn_ok.clicked.connect(self.on_pbn_ok_clicked)
        self.pbn_cancel.clicked.connect(self.on_pbn_cancel_clicked)

    def on_pbn_browse_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择", "../",
                                                            filter="KeePass 2 数据库 (*.kdbx);;所有文件 (*)")
        if len(filename) == 0:
            return
        self.lne_path.setText(filename)

    def on_pbn_eye_clicked(self):
        if self.lne_password.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
            self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.pbn_eye.setIcon(self.icon_eye)
        else:
            self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.pbn_eye.setIcon(self.icon_eye_off)

    def sizeHint(self):
        return QtCore.QSize(540, 40)

    def on_pbn_ok_clicked(self):
        self.accept()

    def on_pbn_cancel_clicked(self):
        self.reject()



