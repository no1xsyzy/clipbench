import sys
from functools import cached_property
from threading import Lock

from PyQt5 import QtWidgets
from PyQt5.Qt import QApplication
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QTextEdit


class ClipboardWorkbench(QMainWindow):
    def __init__(self):
        super().__init__()

        self.transfer = Lock()

        self.setMinimumSize(QSize(440, 240))
        self.setWindowTitle("Clipboard Workbench")

        self.buffer.move(10, 10)
        self.buffer.resize(400, 200)
        self.buffer.setPlainText(QApplication.clipboard().text())

        QApplication.clipboard().dataChanged.connect(self.clipboard_changed)
        self.buffer.textChanged.connect(self.text_changed)

    @cached_property
    def buffer(self):
        return QTextEdit(self)

    def text_changed(self):
        if self.transfer.locked():
            return
        with self.transfer:
            text = self.buffer.toPlainText()
            QApplication.clipboard().setText(text)

    def clipboard_changed(self):
        if self.transfer.locked() or QApplication.clipboard().ownsClipboard():
            return
        with self.transfer:
            text = QApplication.clipboard().text()
            self.buffer.setPlainText(text)


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_win = ClipboardWorkbench()
    main_win.show()
    sys.exit(app.exec_())
