# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui


class GbxKpsLogin(QtWidgets.QGroupBox):
    def __init__(self, path: str, parent=None):
        super().__init__(parent)
        self.is_loaded = False

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

        self.pbn_load = PushButtonWithItem(self, self, "加载")
        self.hly_bottom.addWidget(self.pbn_load)
        self.pbn_remove = PushButtonWithItem(self, self, "移除")
        self.hly_bottom.addWidget(self.pbn_remove)

        self.pbn_eye.clicked.connect(self.on_pbn_eye_clicked)

    def on_pbn_eye_clicked(self):
        is_pass_mode = self.lne_password.echoMode() == QtWidgets.QLineEdit.EchoMode.Password
        if is_pass_mode:
            self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.pbn_eye.setIcon(self.icon_eye)
        else:
            self.lne_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.pbn_eye.setIcon(self.icon_eye_off)


class PushButtonWithItem(QtWidgets.QPushButton):

    clicked_with_item = QtCore.Signal(GbxKpsLogin)

    def __init__(self, item: GbxKpsLogin, parent: QtWidgets.QWidget = None, title: str = ""):
        super().__init__(title, parent)
        self.item = item
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_item.emit(self.item)


class WgLoadKps(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)
        self.vly_m.addStretch(1)

    def add_kps(self, path: str):
        wg = GbxKpsLogin(path, self)
        wg.pbn_remove.clicked_with_item.connect(self.on_item_pbn_remove_clicked)
        wg.pbn_load.clicked_with_item.connect(self.on_item_pbn_load_clicked)
        # 从倒数第二个位置插入，保证弹簧始终在最后
        self.vly_m.insertWidget(self.vly_m.count() - 1, wg)

    def on_item_pbn_remove_clicked(self, item: GbxKpsLogin):
        self.vly_m.removeWidget(item)
        item.deleteLater()

    def on_item_pbn_load_clicked(self, item: GbxKpsLogin):
        item.is_loaded = True
        item.lb_loaded.setVisible(True)
        item.pbn_load.setDisabled(True)


class TabLoad(QtWidgets.QWidget):
    def __init__(self, parent=None):
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
        self.wg_sa = WgLoadKps(self.sa)
        self.sa.setWidget(self.wg_sa)

        self.hly_m.setStretchFactor(self.vly_left, 1)
        self.hly_m.setStretchFactor(self.sa, 6)

        self.pbn_add.clicked.connect(self.on_pbn_add_clicked)

    def on_pbn_add_clicked(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "选择", "../",
                                                              filter="KeePass 2 数据库 (*.kdbx);;所有文件(*)")
        if len(filenames) == 0:
            return
        for filename in filenames:
            self.wg_sa.add_kps(filename)


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
