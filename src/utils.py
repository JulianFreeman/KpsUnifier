# coding: utf8
from PySide6 import QtWidgets


def accept_warning(widget: QtWidgets.QWidget, condition: bool,
                   caption: str = "Warning", text: str = "Are you sure to continue?") -> bool:
    if condition:
        b = QtWidgets.QMessageBox.question(widget, caption, text)
        if b == QtWidgets.QMessageBox.StandardButton.No:
            return True
    return False


class HorizontalLine(QtWidgets.QFrame):

    def __init__(self, parent: QtWidgets.QWidget = None):
        super().__init__(parent)
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)


def get_filepath_uuids_map(query_results: list[list]) -> dict[str, list[str]]:
    file_uuids: dict[str, list[str]] = {}
    for u, filepath in query_results:
        filepath = filepath.decode("utf8")
        if filepath not in file_uuids:
            file_uuids[filepath] = []
        file_uuids[filepath].append(u)

    return file_uuids
