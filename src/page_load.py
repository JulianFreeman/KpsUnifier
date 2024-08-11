# coding: utf8
import sqlite3
from pathlib import Path
from PySide6 import QtWidgets
from pykeepass import PyKeePass

from .gbx_kps_login import GbxKpsLogin
from .utils import accept_warning, HorizontalLine
from lib.Sqlite3Helper import Sqlite3Worker


class WgLoadKps(QtWidgets.QWidget):
    def __init__(
            self,
            config: dict,
            file_kp: dict[str, PyKeePass],
            sqh: Sqlite3Worker,
            sec_sqh: Sqlite3Worker,
            parent: QtWidgets.QWidget = None
    ):
        super().__init__(parent)
        self.sqh = sqh
        self.sec_sqh = sec_sqh
        self.config = config
        self.file_kp = file_kp
        self.kps_wgs: list[GbxKpsLogin] = []

        self.vly_m = QtWidgets.QVBoxLayout()
        self.setLayout(self.vly_m)
        self.vly_m.addStretch(1)

    def update_load_status(self, wg: GbxKpsLogin):
        db_name = Path(self.sqh.db_name).name
        loaded_mem = self.config["loaded_memory"]
        if db_name in loaded_mem and wg.lne_path.text() in loaded_mem[db_name]:
            wg.set_loaded(True)
        else:
            wg.set_loaded(False)

    def add_kps(self, path: str):
        for wg in self.kps_wgs:
            if wg.path == path:
                QtWidgets.QMessageBox.warning(self, "警告", "该 KPS 文件已添加。")
                return

        wg = GbxKpsLogin(path, self.config, self.file_kp, self.sqh, self.sec_sqh, self)
        wg.pbn_remove.clicked_with_item.connect(self.on_item_pbn_remove_clicked)
        # 从倒数第二个位置插入，保证弹簧始终在最后
        self.vly_m.insertWidget(self.vly_m.count() - 1, wg)
        self.kps_wgs.append(wg)

        # 检查是否已经加载过
        self.update_load_status(wg)

    def on_item_pbn_remove_clicked(self, item: GbxKpsLogin):
        self.vly_m.removeWidget(item)
        self.kps_wgs.remove(item)
        item.deleteLater()

    def update_sqh(self, sqh: Sqlite3Worker):
        self.sqh = sqh
        for wg in self.kps_wgs:
            self.update_load_status(wg)


class PageLoad(QtWidgets.QWidget):
    def __init__(
            self,
            config: dict,
            file_kp: dict[str, PyKeePass],
            sqh: Sqlite3Worker,
            sec_sqh: Sqlite3Worker,
            parent: QtWidgets.QWidget = None,
    ):
        super().__init__(parent)
        self.sqh = sqh
        self.config = config

        self.hly_m = QtWidgets.QHBoxLayout()
        self.setLayout(self.hly_m)
        self.vly_left = QtWidgets.QVBoxLayout()
        self.hly_m.addLayout(self.vly_left)

        self.hln_1 = HorizontalLine(self)
        self.vly_left.addWidget(self.hln_1)

        self.pbn_add_kps = QtWidgets.QPushButton("添加 KPS", self)
        self.pbn_add_kps.setMinimumWidth(config["button_min_width"])
        self.vly_left.addWidget(self.pbn_add_kps)

        self.pbn_clear_db = QtWidgets.QPushButton("清空数据库", self)
        self.pbn_clear_db.setMinimumWidth(config["button_min_width"])
        self.vly_left.addWidget(self.pbn_clear_db)

        self.pbn_clear_loaded_mem = QtWidgets.QPushButton("清空加载记忆", self)
        self.pbn_clear_loaded_mem.setMinimumWidth(config["button_min_width"])
        self.vly_left.addWidget(self.pbn_clear_loaded_mem)

        self.vly_left.addStretch(1)

        self.sa_m = QtWidgets.QScrollArea(self)
        self.sa_m.setWidgetResizable(True)
        self.hly_m.addWidget(self.sa_m)
        self.wg_sa = WgLoadKps(config, file_kp, sqh, sec_sqh, self.sa_m)
        self.sa_m.setWidget(self.wg_sa)

        self.pbn_add_kps.clicked.connect(self.on_pbn_add_kps_clicked)
        self.pbn_clear_db.clicked.connect(self.on_pbn_clear_db_clicked)
        self.pbn_clear_loaded_mem.clicked.connect(self.on_pbn_clear_loaded_mem_clicked)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.sqh = sqh
        self.wg_sa.update_sqh(sqh)

    def on_pbn_add_kps_clicked(self):
        filenames, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "选择", self.config["last_open_path"],
                                                              filter="KeePass 2 数据库 (*.kdbx);;所有文件 (*)")
        if len(filenames) == 0:
            return
        for filename in filenames:
            self.wg_sa.add_kps(filename)
        self.config["last_open_path"] = str(Path(filenames[0]).parent)

    def on_pbn_clear_db_clicked(self):
        if accept_warning(self, True, "警告", "你确定要清空当前数据库吗？"):
            return

        try:
            self.sqh.delete_from("entries")
        except sqlite3.OperationalError as e:
            QtWidgets.QMessageBox.critical(self, "错误", f"清空数据库失败：\n{e}")
        else:
            QtWidgets.QMessageBox.information(self, "提示", "已清空数据库")

            # 清空配置文件加载记忆
            loaded_mem = self.config["loaded_memory"]
            db_name = Path(self.sqh.db_name).name
            if db_name in loaded_mem:
                loaded_mem[db_name].clear()

            # 更新kps加载状态
            for wg in self.wg_sa.kps_wgs:
                self.wg_sa.update_load_status(wg)

    def on_pbn_clear_loaded_mem_clicked(self):
        if accept_warning(self, True, "警告", "你确定要清空当前加载记忆吗？"):
            return

        filename = str(Path(self.sqh.db_name).name)
        loaded_mem: list = self.config["loaded_memory"].get(filename, None)
        if loaded_mem is None:
            QtWidgets.QMessageBox.warning(self, "警告", f"没有找到 {filename} 的加载记忆")
        else:
            loaded_mem.clear()
            QtWidgets.QMessageBox.information(self, "提示", "已清空加载记忆")

        # 更新kps加载状态
        for wg in self.wg_sa.kps_wgs:
            self.wg_sa.update_load_status(wg)
