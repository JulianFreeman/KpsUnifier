# coding: utf8
from itertools import combinations
from PySide6 import QtWidgets, QtCore
from PySide6.QtCore import QAbstractTableModel

from .utils import accept_warning, get_filepath_uuids_map, HorizontalLine
from lib.Sqlite3Helper import Sqlite3Worker, Operand
from lib.db_columns_def import sim_columns, filepath_col
from lib.config_utils import path_not_exist
from lib.kps_operations import blob_fy


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

        self.hln_1 = HorizontalLine(self)
        self.vly_left.addWidget(self.hln_1)

        self.pbn_read_db = QtWidgets.QPushButton("读取数据库", self)
        self.pbn_read_db.setMinimumWidth(config["button_min_width"])
        self.vly_left.addWidget(self.pbn_read_db)

        self.pbn_delete_invalid_data = QtWidgets.QPushButton("删除无效文件数据", self)
        self.pbn_delete_invalid_data.setMinimumWidth(config["button_min_width"])
        self.vly_left.addWidget(self.pbn_delete_invalid_data)

        self.vly_left.addStretch(1)

        self.tbv_m = QtWidgets.QTableView(self)
        self.hly_m.addWidget(self.tbv_m)

        self.pbn_read_db.clicked.connect(self.on_pbn_read_db_clicked)
        self.pbn_delete_invalid_data.clicked.connect(self.on_pbn_delete_invalid_data_clicked)

    def on_pbn_read_db_clicked(self):
        _, results = self.sqh.select("entries", sim_columns)
        file_uuids = get_filepath_uuids_map(results)

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

    def on_pbn_delete_invalid_data_clicked(self):
        if accept_warning(self, True, "警告", "你确定要从数据库删除无效文件的记录吗？"):
            return

        _, filepaths = self.sqh.select("entries", [filepath_col,])
        unique_filepaths = set([p[0].decode("utf8") for p in filepaths])
        invalid_filepaths = [p for p in unique_filepaths if path_not_exist(p)]
        for path in invalid_filepaths:
            self.sqh.delete_from("entries",
                                 where=Operand(filepath_col).equal_to(blob_fy(path)),
                                 commit=False)
        self.sqh.commit()
