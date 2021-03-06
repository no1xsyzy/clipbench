import enum
import shlex
import sys
import traceback
from functools import cached_property
from threading import Lock

from PyQt5.QtCore import QSize, QMimeData, QItemSelectionModel, QByteArray
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QGridLayout, QListWidget, QLineEdit, QHBoxLayout, QWidget, QMessageBox,
)

from .editors import possible_editors
from .processors import run


class SyncDirection(str, enum.Enum):
    NO = ''
    BUFFER_TO_CLIPBOARD = 'BUFFER_TO_CLIPBOARD'
    CLIPBOARD_TO_BUFFER = 'CLIPBOARD_TO_BUFFER'
    FREEZE = 'FREEZE'


class ClipboardWorkbench(QMainWindow):
    def __init__(self):
        super().__init__()

        self._transfer = Lock()
        self._sync_direction = SyncDirection.NO
        self._possible_editors = []
        self._current_editor = None
        self._buffer = None
        self._mime_data = {}

        self.setMinimumSize(QSize(440, 240))
        self.setWindowTitle("Clipboard Workbench")

        self.setCentralWidget(self.central_widget)

        self.clipboard_changed()
        QApplication.clipboard().dataChanged.connect(self.clipboard_changed)
        self.mime_select.currentRowChanged.connect(self.mime_select_changed)
        self.command_line.returnPressed.connect(self.run_command)

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
        grid_layout.addWidget(self.command_line, 2, 1)
        grid_layout.addWidget(self.operation_select, 1, 2, 2, 1)
        return grid_layout

    @property
    def buffer(self):
        assert self._buffer is not None, "buffer get before set"
        return self._buffer

    @buffer.setter
    def buffer(self, new_buffer):
        old_buffer = self._buffer
        self._buffer = new_buffer
        if old_buffer is not None:
            self.grid_layout.removeWidget(old_buffer.widget)
            old_buffer.changed.disconnect()
        self.grid_layout.addWidget(new_buffer.widget, 1, 1)
        new_buffer.changed.connect(self.text_changed)

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
    def mime_data(self):
        return self._mime_data

    @mime_data.setter
    def mime_data(self, value):
        if isinstance(value, QMimeData):
            self._mime_data = {fmt: value.data(fmt) for fmt in value.formats()}
        else:
            self._mime_data = value
        self._possible_editors = [
            ((f"{f} |> {e}" if e else f), b)
            for row, (f, e, b) in enumerate(possible_editors(self._mime_data))
        ]
        self.mime_select.clear()
        rows = [fe for fe, b in self._possible_editors]
        self.mime_select.addItems(rows)
        if not self._mime_data:
            self.current_editor = None
        elif self.current_editor not in rows:
            for fmt in ['text/plain', 'text/html', 'application/x-qt-windows-mime;value="Rich Text Format"']:
                if fmt in self._possible_editors:
                    self.current_editor = fmt
                    break
            else:
                if rows:
                    self.current_editor = rows[0]
        else:
            self.current_editor = self.current_editor

    @property
    def current_editor(self):
        return self._current_editor

    @current_editor.setter
    def current_editor(self, value):
        self._current_editor = value
        if value is None:
            self.mime_select.setCurrentRow(0, QItemSelectionModel.Deselect)
        else:
            self.mime_select.setCurrentRow([fe for fe, b in self._possible_editors].index(value))

    @property
    def current_format(self):
        if " |> " in self.current_editor:
            return self.current_editor.split(" |> ", 1)[0]
        else:
            return self.current_editor

    def text_changed(self):
        if self._transfer.locked() or self._sync_direction != SyncDirection.NO:
            return
        with self._transfer:
            self._sync_direction = SyncDirection.BUFFER_TO_CLIPBOARD
            self.sync_buffer_to_clipboard()
            self._sync_direction = SyncDirection.NO

    def mime_select_changed(self, row):
        if self._transfer.locked() or self._sync_direction != SyncDirection.NO:
            return
        with self._transfer:
            self._sync_direction = SyncDirection.CLIPBOARD_TO_BUFFER
            fe, b = self._possible_editors[row]
            self._current_editor = fe
            self.buffer = b()
            self.sync_clipboard_to_buffer()
            self._sync_direction = SyncDirection.NO

    def clipboard_changed(self):
        clipboard = QApplication.clipboard()
        if self._transfer.locked() or clipboard.ownsClipboard() or self._sync_direction != SyncDirection.NO:
            return
        with self._transfer:
            self._sync_direction = SyncDirection.CLIPBOARD_TO_BUFFER
            mime = clipboard.mimeData()
            self.mime_data = mime
            if self.mime_select.currentRow() >= 0:
                fe, b = self._possible_editors[self.mime_select.currentRow()]
                self._current_editor = fe
                self.buffer = b()
                self.sync_clipboard_to_buffer()
            self._sync_direction = SyncDirection.NO

    def sync_buffer_to_clipboard(self):
        assert self._sync_direction == SyncDirection.BUFFER_TO_CLIPBOARD
        data = self.buffer.get_content()
        self.mime_data = {self.current_format: data}
        mimedata = QMimeData()
        mimedata.setData(self.current_format, data)
        QApplication.clipboard().setMimeData(mimedata)

    def sync_clipboard_to_buffer(self):
        assert self._sync_direction == SyncDirection.CLIPBOARD_TO_BUFFER
        byte_data = self.mime_data[self.current_format]
        if isinstance(byte_data, QByteArray):
            byte_data = byte_data.data()
        self.buffer.set_content(byte_data)

    def run_command(self):
        command = self.command_line.text()
        split = shlex.split(command)
        # noinspection PyBroadException
        # since it is showing the exception to user
        try:
            run(split, self)
        except Exception:
            msg = QMessageBox()
            msg.setWindowTitle("ClipBench")
            msg.setText(''.join(traceback.format_exception_only(*sys.exc_info()[:2])))
            msg.setInformativeText(traceback.format_exc())
            msg.exec_()
            self.command_line.selectAll()
        else:
            self.command_line.setText("")


def main():
    app = QApplication(sys.argv)
    main_win = ClipboardWorkbench()
    main_win.show()
    sys.exit(app.exec_())
