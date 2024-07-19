# coding: utf8
from itertools import combinations
from uuid import UUID
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QAbstractTableModel

from lib.Sqlite3Helper import Sqlite3Worker
from lib.db_columns_def import sim_columns


class SimilarDataModel(QAbstractTableModel):
    def __init__(self, similar_data: list[tuple], parent=None):
        super().__init__(parent)
        self.similar_data = similar_data
        self.headers = ["文件1", "文件2", "相似度"]

    def rowCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.similar_data)

    def columnCount(self, parent: QtCore.QModelIndex = ...):
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex, role: int = ...):
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.similar_data[index.row()][index.column()]
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            if index.column() == 2:
                return QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter

    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = ...):
        if orientation == QtCore.Qt.Orientation.Horizontal:
            if role == QtCore.Qt.ItemDataRole.DisplayRole:
                return self.headers[section]


class PageSimilar(QtWidgets.QWidget):
    def __init__(
            self,
            sqh: Sqlite3Worker,
            config: dict,
            parent: QtWidgets.QWidget = None
    ):
        super().__init__(parent)
        self.sqh = sqh
        self.config = config

        self.hly_m = QtWidgets.QHBoxLayout()
        self.setLayout(self.hly_m)

        self.vly_left = QtWidgets.QVBoxLayout()
        self.hly_m.addLayout(self.vly_left)

        self.pbn_read_db = QtWidgets.QPushButton("读取数据库", self)
        self.pbn_read_db.setMinimumWidth(config["button_min_width"])
        self.vly_left.addWidget(self.pbn_read_db)

        self.vly_left.addStretch(1)

        self.tbv_m = QtWidgets.QTableView(self)
        self.hly_m.addWidget(self.tbv_m)

        self.pbn_read_db.clicked.connect(self.on_pbn_read_db_clicked)

    def on_pbn_read_db_clicked(self):
        _, results = self.sqh.select(self.config["table_name"], sim_columns)
        file_uuids: dict[str, list[UUID]] = {}
        for u, filepath in results:
            filepath = filepath.decode("utf8")
            if filepath not in file_uuids:
                file_uuids[filepath] = []
            file_uuids[filepath].append(u)

        files = file_uuids.keys()
        if len(files) < 2:
            QtWidgets.QMessageBox.warning(self, "警告", "数据库中存在的文件数少于 2，无法检查相似度。")
            return

        similar_data: list[tuple] = []

        comb = combinations(files, 2)
        for i, j in list(comb):
            uuids_i = file_uuids[i]
            uuids_j = file_uuids[j]
            len_i = len(uuids_i)
            len_j = len(uuids_j)

            set_inter = set(uuids_i).intersection(uuids_j)
            sim = (len(set_inter) * 2) / (len_i + len_j)
            similar_data.append((i, j, f"{sim * 100:.2f}"))

        model = SimilarDataModel(similar_data, self)
        self.tbv_m.setModel(model)
