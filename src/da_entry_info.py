# coding: utf8
from PySide6 import QtWidgets, QtCore, QtGui

from lib.Sqlite3Helper import Sqlite3Worker, Operand
from lib.db_columns_def import entry_id_col, all_columns


class UiDaEntryInfo(object):
    def __init__(
            self,
            entry_info: dict,
            window: QtWidgets.QDialog
    ):
        self.entry_info = entry_info
        self.window = window
        window.setWindowTitle("条目信息")

        self.vly_m = QtWidgets.QVBoxLayout()
        window.setLayout(self.vly_m)

        self.add_line("标题：", entry_info["title"])
        self.add_line("用户名：", entry_info["username"])
        self.add_line("密码：", entry_info["password"], is_secret=True)
        self.add_line("TOTP：", entry_info["opt"], is_secret=True)
        self.add_line("URL：", entry_info["url"])
        self.add_line("文件路径：", entry_info["filepath"])
        self.add_line("条目位置：", entry_info["path"])

        # 备注单独整
        self.hly_notes = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(self.hly_notes)
        self.lb_notes = QtWidgets.QLabel("备注：", window)
        self.lb_notes.setMinimumWidth(60)
        self.lb_notes.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        self.pte_notes = QtWidgets.QPlainTextEdit(entry_info["notes"].decode("utf-8"), window)
        self.hly_notes.addWidget(self.lb_notes)
        self.hly_notes.addWidget(self.pte_notes)

    def add_line(self, label: str, lne_content: str | bytes, is_secret: bool = False):
        if isinstance(lne_content, bytes):
            lne_content = lne_content.decode("utf-8")

        hly_1 = QtWidgets.QHBoxLayout()
        self.vly_m.addLayout(hly_1)
        lb_1 = QtWidgets.QLabel(label, self.window)
        lb_1.setMinimumWidth(60)
        lne_1 = QtWidgets.QLineEdit(lne_content, self.window)
        hly_1.addWidget(lb_1)
        hly_1.addWidget(lne_1)

        if is_secret:
            lne_1.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

            icon_eye = QtGui.QIcon(":/asset/img/eye.svg")
            icon_eye_off = QtGui.QIcon(":/asset/img/eye-off.svg")
            pbn_eye = QtWidgets.QPushButton(icon=icon_eye_off, parent=self.window)
            hly_1.addWidget(pbn_eye)

            def on_pbn_eye_clicked():
                if lne_1.echoMode() == QtWidgets.QLineEdit.EchoMode.Password:
                    lne_1.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
                    pbn_eye.setIcon(icon_eye)
                else:
                    lne_1.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
                    pbn_eye.setIcon(icon_eye_off)

            pbn_eye.clicked.connect(on_pbn_eye_clicked)


class DaEntryInfo(QtWidgets.QDialog):
    def __init__(
            self,
            entry_id: int,
            config: dict,
            sqh: Sqlite3Worker,
            parent: QtWidgets.QWidget = None
    ):
        super().__init__(parent)
        _, results = sqh.select(config["table_name"], all_columns,
                                where=Operand(entry_id_col).equal_to(entry_id))

        entry = results[0]
        assert len(entry) == len(all_columns)

        entry_info = {all_columns[i].name: entry[i] for i in range(len(all_columns))}

        self.ui = UiDaEntryInfo(entry_info, self)

    def sizeHint(self):
        return QtCore.QSize(640, 360)


