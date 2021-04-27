from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QWidget


class BaseBuffer(QObject):
    widget: QWidget

    def set_content(self, content: bytes): ...

    def get_content(self) -> bytes: ...

    changed = pyqtSignal()
