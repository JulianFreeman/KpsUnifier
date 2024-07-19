# coding: utf8
import json

from PySide6 import QtWidgets, QtCore, QtGui
from lib.Sqlite3Helper import Sqlite3Worker, Operand, Expression
from lib.db_columns_def import query_columns
from lib.global_config import button_min_width, table_name


class QueryTableModel(QtCore.QAbstractTableModel):

    def __init__(self, query_results: list[tuple], parent=None):
        super().__init__(parent)
        self.query_results = query_results
        self.headers = ["序号", "标题", "用户名", "URL"]

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

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self.headers[section]


class PageQuery(QtWidgets.QWidget):
    def __init__(self, sqh: Sqlite3Worker, parent=None):
        super().__init__(parent)
        self.sqh = sqh

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
        self.pbn_all.setMinimumWidth(button_min_width)
        self.vly_sa_wg.addWidget(self.pbn_all)

        self.vly_sa_wg.addStretch(1)

        self.pbn_read_filters = QtWidgets.QPushButton("更多过滤", self)
        self.pbn_read_filters.setMinimumWidth(button_min_width)
        self.vly_sa_wg.addWidget(self.pbn_read_filters)

        self.trv_m = QtWidgets.QTreeView(self)
        # self.trv_m.setSortingEnabled(True)
        self.hly_m.addWidget(self.trv_m)

        self.pbn_all.clicked.connect(self.on_pbn_all_clicked)
        self.pbn_read_filters.clicked.connect(self.on_pbn_read_filters_clicked)

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
        pbn_fil.setMinimumWidth(button_min_width)
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
        _, results = self.sqh.select(table_name, query_columns, where=Expression(data["where"]))
        model = QueryTableModel(results, self)
        self.trv_m.setModel(model)

    def update_sqh(self, sqh: Sqlite3Worker):
        self.sqh = sqh

    def on_pbn_all_clicked(self):
        _, results = self.sqh.select(table_name, query_columns)
        model = QueryTableModel(results, self)
        self.trv_m.setModel(model)


class PushButtonWithData(QtWidgets.QPushButton):

    clicked_with_data = QtCore.Signal(dict)

    def __init__(self, data: dict, parent: QtWidgets.QWidget = None, title: str = ""):
        super().__init__(title, parent)
        self.data = data
        self.clicked.connect(self.on_self_clicked)

    def on_self_clicked(self):
        self.clicked_with_data.emit(self.data)
