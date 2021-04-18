import sys
from functools import cached_property
from threading import Lock

from PyQt5 import QtWidgets
from PyQt5.Qt import QApplication
from PyQt5.QtCore import QSize, QMimeData, QItemSelectionModel, QByteArray
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QGridLayout, QListWidget, QLineEdit, QHBoxLayout, QWidget

from .hexdump import to_hex_dump, from_hex_dump

BUFFER_TO_CLIPBOARD = 'BUFFER_TO_CLIPBOARD'
CLIPBOARD_TO_BUFFER = 'CLIPBOARD_TO_BUFFER'


class ClipboardWorkbench(QMainWindow):
    def __init__(self):
        super().__init__()

        self._transfer = Lock()
        self._sync_direction = ''
        self._formats = []
        self._current_format = None
        self.format_data = {}

        self.setMinimumSize(QSize(440, 240))
        self.setWindowTitle("Clipboard Workbench")

        self.setCentralWidget(self.central_widget)

        self.clipboard_changed()
        QApplication.clipboard().dataChanged.connect(self.clipboard_changed)
        self.buffer.textChanged.connect(self.text_changed)
        self.mime_select.currentRowChanged.connect(self.mime_select_changed)

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
        return grid_layout

    @cached_property
    def buffer(self):
        buffer = QTextEdit()
        return buffer

    @cached_property
    def mime_select(self) -> QListWidget:
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

    @property
    def formats(self):
        return self._formats

    @formats.setter
    def formats(self, value):
        self._formats = value
        self.mime_select.clear()
        self.mime_select.addItems(self.formats)
        if not value:
            self.current_format = None
        elif self.current_format not in value:
            for fmt in ['text/plain', 'text/html', 'application/x-qt-windows-mime;value="Rich Text Format"']:
                if fmt in value:
                    self.current_format = fmt
                    break
            else:
                self.current_format = value[0]

    @property
    def current_format(self):
        return self._current_format

    @current_format.setter
    def current_format(self, value):
        self._current_format = value
        if self.current_format is None:
            self.mime_select.setCurrentRow(0, QItemSelectionModel.Deselect)
        else:
            self.mime_select.setCurrentRow(self.formats.index(self.current_format))

    def text_changed(self):
        if self._transfer.locked():
            return
        with self._transfer:
            self._sync_direction = BUFFER_TO_CLIPBOARD
            self.sync_buffer_to_clipboard()
            self._sync_direction = None

    def mime_select_changed(self, row):
        if self._transfer.locked():
            return
        with self._transfer:
            self._sync_direction = CLIPBOARD_TO_BUFFER
            self._current_format = self.formats[row]
            self.sync_clipboard_to_buffer()
            self._sync_direction = None

    def clipboard_changed(self):
        clipboard = QApplication.clipboard()
        if self._transfer.locked() or clipboard.ownsClipboard():
            return
        with self._transfer:
            self._sync_direction = CLIPBOARD_TO_BUFFER
            mime = clipboard.mimeData()
            self.formats = mime.formats()
            self.format_data = {fmt: mime.data(fmt) for fmt in self.formats}
            self.sync_clipboard_to_buffer()
            self._sync_direction = None

    def sync_buffer_to_clipboard(self):
        assert self._sync_direction == BUFFER_TO_CLIPBOARD
        self.formats = [self.current_format]
        self.format_data = {self.current_format: self.format_data[self.current_format]}
        if self.current_format == 'text/plain':
            data = self.buffer.toPlainText().encode('utf-8')
        elif self.current_format == 'text/html':
            data = self.buffer.toHtml().encode('utf-8')
        else:
            data = from_hex_dump(self.buffer.toPlainText())
        self.format_data = {self.current_format: data}
        mimedata = QMimeData()
        mimedata.setData(self.current_format, data)
        QApplication.clipboard().setMimeData(mimedata)

    def sync_clipboard_to_buffer(self):
        assert self._sync_direction == CLIPBOARD_TO_BUFFER
        byte_data = self.format_data[self.current_format]
        if isinstance(byte_data, QByteArray):
            byte_data = byte_data.data()
        if self.current_format == 'text/plain':
            self.buffer.setPlainText(byte_data.decode('utf-8'))
        elif self.current_format == 'text/html':
            self.buffer.setHtml(byte_data.decode('utf-8'))
        else:
            self.buffer.setPlainText(to_hex_dump(byte_data))


def main():
    app = QtWidgets.QApplication(sys.argv)
    main_win = ClipboardWorkbench()
    main_win.show()
    sys.exit(app.exec_())
