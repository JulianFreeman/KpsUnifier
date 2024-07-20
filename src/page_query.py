# coding: utf8
import json
from PySide6 import QtWidgets, QtCore, QtGui

from .da_entry_info import DaEntryInfo
from lib.Sqlite3Helper import Sqlite3Worker, Expression, Operand
from lib.db_columns_def import query_columns, status_col, entry_id_col


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
            "keep": QtGui.QBrush(QtGui.QColor("green")),
            "transfer": QtGui.QBrush(QtGui.QColor("orange")),
            "delete": QtGui.QBrush(QtGui.QColor("orangered")),
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


class PageQuery(QtWidgets.QWidget):
    def __init__(self, sqh: Sqlite3Worker, config: dict, parent=None):
        super().__init__(parent)
        self.sqh = sqh
        self.config = config

        # 右键菜单
        self.menu_ctx = QtWidgets.QMenu(self)
        self.act_keep = ActionWithStr("keep", "保留", self)
        self.act_transfer = ActionWithStr("transfer", "转移", self)
        self.act_delete = ActionWithStr("delete", "删除", self)
        self.menu_ctx.addActions([self.act_keep, self.act_transfer, self.act_delete])

        self.act_keep.triggered_with_str.connect(self.on_act_mark_triggered_with_str)
        self.act_transfer.triggered_with_str.connect(self.on_act_mark_triggered_with_str)
        self.act_delete.triggered_with_str.connect(self.on_act_mark_triggered_with_str)

        # 主布局

        self.hly_m = QtWidgets.QHBoxLayout()
        self.setLayout(self.hly_m)

        self.sa_left = QtWidgets.QScrollArea(self)
        self.sa_left.setWidgetResizable(True)
        self.sa_left.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sa_left.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Ignored)
        self.hly_m.addWidget(self.sa_left)

        self.sa_wg = QtWidgets.QWidget(self.sa_left)
        self.vly_sa_wg = QtWidgets.QVBoxLayout()
        self.sa_wg.setLayout(self.vly_sa_wg)
        self.sa_left.setWidget(self.sa_wg)

        self.pbn_all = QtWidgets.QPushButton("全部", self.sa_wg)
        self.pbn_all.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_all)

        self.vly_sa_wg.addStretch(1)

        self.pbn_read_filters = QtWidgets.QPushButton("更多过滤", self)
        self.pbn_read_filters.setMinimumWidth(config["button_min_width"])
        self.vly_sa_wg.addWidget(self.pbn_read_filters)

        self.trv_m = QtWidgets.QTreeView(self)
        self.trv_m.setSelectionMode(QtWidgets.QTreeView.SelectionMode.ExtendedSelection)
        self.trv_m.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        # self.trv_m.setSortingEnabled(True)
        self.hly_m.addWidget(self.trv_m)

        self.pbn_all.clicked.connect(self.on_pbn_all_clicked)
        self.pbn_read_filters.clicked.connect(self.on_pbn_read_filters_clicked)
        self.trv_m.doubleClicked.connect(self.on_trv_m_double_clicked)
        self.trv_m.customContextMenuRequested.connect(self.on_trv_m_custom_context_menu_requested)

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
        pbn_fil = PushButtonWithData(fil, self.sa_wg, fil["name"])
        pbn_fil.setMinimumWidth(self.config["button_min_width"])
        self.vly_sa_wg.insertWidget(self.vly_sa_wg.count() - 2, pbn_fil)
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
                                     where=Expression(data["where"]))
        model = QueryTableModel(results, self)
        self.trv_m.setModel(model)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.sqh = sqh

    def on_pbn_all_clicked(self):
        _, results = self.sqh.select(self.config["table_name"], query_columns)
        model = QueryTableModel(results, self)
        self.trv_m.setModel(model)

    def on_trv_m_double_clicked(self, index: QtCore.QModelIndex):
        entry_id = index.siblingAtColumn(0).data(QtCore.Qt.ItemDataRole.DisplayRole)
        da_entry_info = DaEntryInfo(entry_id, self.config, self.sqh, self)
        da_entry_info.exec()

    def on_trv_m_custom_context_menu_requested(self, pos: QtCore.QPoint):
        self.menu_ctx.exec(self.trv_m.viewport().mapToGlobal(pos))

    def on_act_mark_triggered_with_str(self, info: str):
        indexes = self.trv_m.selectedIndexes()
        entry_ids = [
            index.data(QtCore.Qt.ItemDataRole.DisplayRole)
            for index in indexes if index.column() == 0
        ]

        self.sqh.update(self.config["table_name"], [(status_col, info)],
                        where=Operand(entry_id_col).in_(entry_ids))


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
