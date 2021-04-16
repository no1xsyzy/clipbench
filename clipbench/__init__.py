import sys
from functools import cached_property
from threading import Lock

from PyQt5 import QtWidgets
from PyQt5.Qt import QApplication
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QGridLayout, QListWidget, QLineEdit, QHBoxLayout, QWidget


class ClipboardWorkbench(QMainWindow):
    def __init__(self):
        super().__init__()

        self.transfer = Lock()

        self.setMinimumSize(QSize(440, 240))
        self.setWindowTitle("Clipboard Workbench")

        self.setCentralWidget(self.central_widget)

        self.buffer.setPlainText(QApplication.clipboard().text())
        QApplication.clipboard().dataChanged.connect(self.clipboard_changed)
        self.buffer.textChanged.connect(self.text_changed)

    @cached_property
    def central_widget(self):
        central_widget = QWidget()
        central_widget.setLayout(self.grid_layout)
        return central_widget

    @cached_property
    def grid_layout(self) -> QGridLayout:
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(5)
        grid_layout.setVerticalSpacing(5)
        grid_layout.addLayout(self.clipboard_select, 0, 0, 1, 3)
        grid_layout.addWidget(self.mime_select, 1, 0, 2, 1)
        grid_layout.addWidget(self.buffer, 1, 1)
        grid_layout.addWidget(self.command_line, 2, 1)
        grid_layout.addWidget(self.operation_select, 1, 2, 2, 1)
        self.setLayout(grid_layout)
        return grid_layout

    @cached_property
    def buffer(self):
        buffer = QTextEdit()
        return buffer

    @cached_property
    def mime_select(self):
        mime_select = QListWidget()
        return mime_select

    @cached_property
    def command_line(self):
        command_line = QLineEdit()
        return command_line

    @cached_property
    def operation_select(self):
        operation_select = QListWidget()
        return operation_select

    @cached_property
    def clipboard_select(self):
        clipboard_select = QHBoxLayout()
        return clipboard_select

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
