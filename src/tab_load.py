# coding: utf8
from PySide6 import QtWidgets
from .gbx_kps_login import GbxKpsLogin


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
