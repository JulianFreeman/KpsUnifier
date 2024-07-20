# coding: utf8
import json
from uuid import UUID
from PySide6 import QtWidgets, QtCore, QtGui
from pykeepass import PyKeePass

from .da_entry_info import DaEntryInfo
from .da_target_login import DaTargetLogin
from .utils import HorizontalLine, get_filepath_uuids_map, accept_warning
from lib.Sqlite3Helper import Sqlite3Worker, Expression, Operand
from lib.db_columns_def import (
    query_columns, status_col, entry_id_col,
    sim_columns, deleted_col, uuid_col, filepath_col,
)
from lib.sec_db_columns_def import sec_password_col, sec_filepath_col
from lib.kps_operations import blob_fy


class QueryTableModel(QtCore.QAbstractTableModel):

    def __init__(self, query_results: list[tuple], parent=None):
        super().__init__(parent)
        self.query_results = query_results
        self.headers = ["序号", "标题", "用户名", "URL"]

        self.light_status_colors = {
            "keep": QtGui.QBrush(QtGui.QColor("lightgreen")),
            "transfer": QtGui.QBrush(QtGui.QColor("moccasin")),
            "delete": QtGui.QBrush(QtGui.QColor("pink")),
            "none": QtGui.QBrush(QtCore.Qt.GlobalColor.transparent)
        }
        self.dark_status_colors = {
            "keep": QtGui.QBrush(QtGui.QColor("forestgreen")),
            "transfer": QtGui.QBrush(QtGui.QColor("darksalmon")),
            "delete": QtGui.QBrush(QtGui.QColor("darkred")),
            "none": QtGui.QBrush(QtCore.Qt.GlobalColor.transparent)
        }
        if QtWidgets.QApplication.style().name() == "windowsvista":
            self.status_colors = self.light_status_colors
        elif QtWidgets.QApplication.styleHints().colorScheme() == QtCore.Qt.ColorScheme.Dark:
            self.status_colors = self.dark_status_colors
        else:
            self.status_colors = self.light_status_colors

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.query_results)

    def columnCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            item = self.query_results[index.row()][index.column()]
            if isinstance(item, bytes):
                return item.decode("utf-8")
            return item
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            status = self.query_results[index.row()][-1]  # 最后一列是状态
            if status is None:
                status = "none"
            return self.status_colors[status]
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == 0:
                return QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self.headers[section]


class UiPageQuery(object):
    def __init__(self, config: dict, window: QtWidgets.QWidget):
        # 右键菜单
        self.menu_ctx = QtWidgets.QMenu(window)
        self.act_keep = ActionWithStr("keep", "保留", window)
        self.act_transfer = ActionWithStr("transfer", "转移", window)
        self.act_delete = ActionWithStr("delete", "删除", window)
        self.menu_ctx.addActions([self.act_keep, self.act_transfer, self.act_delete])

        # 主布局

        self.hly_m = QtWidgets.QHBoxLayout()
        window.setLayout(self.hly_m)

        self.sa_left = QtWidgets.QScrollArea(window)
        self.sa_left.setWidgetResizable(True)
        self.sa_left.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sa_left.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Ignored)
        self.hly_m.addWidget(self.sa_left)

        self.sa_wg = QtWidgets.QWidget(self.sa_left)
        self.vly_sa_wg = QtWidgets.QVBoxLayout()
        self.sa_wg.setLayout(self.vly_sa_wg)
        self.sa_left.setWidget(self.sa_wg)

        self.pbn_execute = QtWidgets.QPushButton("执行操作", window)
        self.pbn_execute.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_execute)

        self.pbn_set_target = QtWidgets.QPushButton("目标文件", window)
        self.pbn_set_target.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_set_target)

        self.hln_1 = HorizontalLine(window)
        self.vly_sa_wg.addWidget(self.hln_1)

        self.pbn_all = QtWidgets.QPushButton("全部", self.sa_wg)
        self.pbn_all.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_all)

        self.pbn_deleted = QtWidgets.QPushButton("已删除", self.sa_wg)
        self.pbn_deleted.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_deleted)

        self.vly_sa_wg.addStretch(1)

        self.pbn_read_filters = QtWidgets.QPushButton("更多过滤", window)
        self.pbn_read_filters.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_read_filters)

        self.trv_m = QtWidgets.QTreeView(window)
        self.trv_m.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ExtendedSelection)
        self.trv_m.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        # self.trv_m.setSortingEnabled(True)
        self.hly_m.addWidget(self.trv_m)


class PageQuery(QtWidgets.QWidget):
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
        self.sec_sqh = sec_sqh
        self.config = config
        self.file_kp = file_kp
        self.ui = UiPageQuery(config, self)

        self.ui.act_keep.triggered_with_str.connect(self.on_act_mark_triggered_with_str)
        self.ui.act_transfer.triggered_with_str.connect(self.on_act_mark_triggered_with_str)
        self.ui.act_delete.triggered_with_str.connect(self.on_act_mark_triggered_with_str)

        self.ui.pbn_execute.clicked.connect(self.on_pbn_execute_clicked)
        self.ui.pbn_set_target.clicked.connect(self.on_pbn_set_target_clicked)

        self.ui.pbn_all.clicked.connect(self.on_pbn_all_clicked)
        self.ui.pbn_deleted.clicked.connect(self.on_pbn_deleted_clicked)
        self.ui.pbn_read_filters.clicked.connect(self.on_pbn_read_filters_clicked)
        self.ui.trv_m.doubleClicked.connect(self.on_trv_m_double_clicked)
        self.ui.trv_m.customContextMenuRequested.connect(self.on_trv_m_custom_context_menu_requested)

        self.set_default_filters()

    def set_default_filters(self):
        default_filters = [
            {
                "name": "Gmail 邮箱",
                "where": "username LIKE '%@gmail.com'"
            },
            {
                "name": "Outlook 邮箱",
                "where": "username LIKE '%@outlook.com'"
            },
            {
                "name": "谷歌文档",
                "where": "url LIKE 'https://docs.google.com/%' or url LIKE 'https://drive.google.com/%'"
            },
        ]
        for fil in default_filters:
            self.set_filter_button(fil)

    def set_filter_button(self, fil: dict):
        pbn_fil = PushButtonWithData(fil, self.ui.sa_wg, fil["name"])
        pbn_fil.setMinimumWidth(self.config["button_min_width"])
        self.ui.vly_sa_wg.insertWidget(self.ui.vly_sa_wg.count() - 2, pbn_fil)
        pbn_fil.clicked_with_data.connect(self.on_custom_filters_clicked_with_data)

    def on_pbn_read_filters_clicked(self):
        filename, _ = QtWidgets.QFileDialog.getOpenFileName(self, "打开", "../",
                                                            filter="JSON 文件 (*.json);;所有文件 (*)")
        if len(filename) == 0:
            return
        with open(filename, "r", encoding="utf8") as f:
            filter_ls: list[dict] = json.load(f)

        for fil in filter_ls:
            self.set_filter_button(fil)

    def on_custom_filters_clicked_with_data(self, data: dict):
        _, results = self.sqh.select(self.config["table_name"], query_columns,
                                     where=Expression(data["where"]).and_(Operand(deleted_col).equal_to(0)))
        model = QueryTableModel(results, self)
        self.ui.trv_m.setModel(model)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.sqh = sqh

    def on_pbn_all_clicked(self):
        _, results = self.sqh.select(self.config["table_name"], query_columns,
                                     where=Operand(deleted_col).equal_to(0))
        model = QueryTableModel(results, self)
        self.ui.trv_m.setModel(model)

    def on_pbn_deleted_clicked(self):
        _, results = self.sqh.select(self.config["table_name"], query_columns,
                                     where=Operand(deleted_col).equal_to(1))
        model = QueryTableModel(results, self)
        self.ui.trv_m.setModel(model)

    def on_trv_m_double_clicked(self, index: QtCore.QModelIndex):
        entry_id = index.siblingAtColumn(0).data(QtCore.Qt.ItemDataRole.DisplayRole)
        da_entry_info = DaEntryInfo(entry_id, self.config, self.sqh, self)
        da_entry_info.exec()

    def on_trv_m_custom_context_menu_requested(self, pos: QtCore.QPoint):
        self.ui.menu_ctx.exec(self.ui.trv_m.viewport().mapToGlobal(pos))

    def on_act_mark_triggered_with_str(self, info: str):
        indexes = self.ui.trv_m.selectedIndexes()
        entry_ids = [
            index.data(QtCore.Qt.ItemDataRole.DisplayRole)
            for index in indexes if index.column() == 0
        ]

        self.sqh.update(self.config["table_name"], [(status_col, info)],
                        where=Operand(entry_id_col).in_(entry_ids))

    def on_pbn_execute_clicked(self):
        if accept_warning(self, True, "警告", "你确定要执行转移和删除操作吗？"):
            return

        # 删除功能
        _, results = self.sqh.select(self.config["table_name"], sim_columns,
                                     where=Operand(status_col).equal_to("delete"))
        file_uuids = get_filepath_uuids_map(results)

        total, success, invalid = 0, 0, 0
        for file in file_uuids:
            if file not in self.file_kp:
                _, results = self.sec_sqh.select("secrets", [sec_password_col],
                                                 where=Operand(sec_filepath_col).equal_to(blob_fy(file)))
                password = results[-1][0].decode("utf-8")
                kp = PyKeePass(file, password)
            else:
                kp = self.file_kp[file]

            for u in file_uuids[file]:
                total += 1
                self.sqh.update(self.config["table_name"], [(deleted_col, 1)],
                                where=Operand(uuid_col).equal_to(u).and_(
                                    Operand(filepath_col).equal_to(blob_fy(file))))

                entry = kp.find_entries(uuid=UUID(u), first=True)
                if entry is None:
                    invalid += 1
                    continue

                kp.delete_entry(entry)
                success += 1

            kp.save()

        QtWidgets.QMessageBox.information(self, "提示",
                                          f"共 {total} 条标记的条目，已删除 {success} 条，无效 {invalid} 条。")

    def on_pbn_set_target_clicked(self):
        da_target_login = DaTargetLogin(self)
        da_target_login.exec()


class PushButtonWithData(QtWidgets.QPushButton):

    clicked_with_data = QtCore.Signal(dict)

    def __init__(self, data: dict, parent: QtWidgets.QWidget = None, title: str = ""):
        super().__init__(title, parent)
        self.data = data
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_data.emit(self.data)


class ActionWithStr(QtGui.QAction):

    triggered_with_str = QtCore.Signal(str)

    def __init__(self, info: str, title: str, parent: QtWidgets.QWidget = None):
        super().__init__(title, parent)
        self.info = info
        self.triggered.connect(self.on_self_triggered)

    def on_self_triggered(self):
        self.triggered_with_str.emit(self.info)
